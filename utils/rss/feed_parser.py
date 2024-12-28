import feedparser
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
import html
from datetime import datetime, timedelta
import time

DEFAULT_IMAGES = {
    'Cointelegraph': {
        'url': 'https://images.cointelegraph.com/cdn-cgi/image/format=auto,onerror=redirect,quality=90,width=370/https://s3.cointelegraph.com/uploads/2023-10/aa1373ce-e0ee-4341-84fa-efb0ca1dc1aa.jpg',
        'format': 'jpeg'
    },
    'Investing.com': {
        'url': 'https://i-invdn-com.investing.com/news/newonInvesting.jpg',
        'format': 'jpeg'
    }
}

@dataclass
class News:
    title: str                    # Título é obrigatório
    url: str                      # URL é obrigatório
    source: str                   # Fonte é obrigatória
    published_time: str           # Data de publicação é obrigatória (formato: YYYY-MM-DD HH:MM:SS)
    summary: Optional[str] = None # Resumo é opcional
    image_url: Optional[str] = None # URL da imagem é opcional
    image_format: Optional[str] = None # Formato da imagem é opcional

class FeedParser:
    def __init__(self, rss_feeds: List[Dict[str, str]]):
        self.rss_feeds = rss_feeds
        self.news = self._parse_feeds()

    def clean_html(self, html_text: str) -> str:
        """Remove tags HTML, decodifica entidades HTML e retorna apenas o texto."""
        if not html_text:
            return ""
            
        # Remove tags de imagem completas
        text = re.sub(r'<p[^>]*>(?:\s*<img[^>]*>\s*)*</p>', '', html_text)
        # Remove todas as outras tags HTML
        text = re.sub(r'<[^>]+>', '', text)
        # Decodifica entidades HTML
        text = html.unescape(text)
        # Remove espaços extras
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def convert_to_local_time(self, parsed_time: time.struct_time) -> str:
        """Converte time.struct_time para string no formato YYYY-MM-DD HH:MM:SS no fuso horário UTC-3."""
        # Converter struct_time para datetime UTC
        utc_time = datetime(*parsed_time[:6])
        
        # Ajustar para UTC-3 (São Paulo)
        local_time = utc_time - timedelta(hours=3)
        
        # Formatar no formato desejado
        return local_time.strftime('%Y-%m-%d %H:%M')

    def _parse_feeds(self) -> List[News]:
        all_news = []
        
        for feed_dict in self.rss_feeds:
            source = list(feed_dict.keys())[0]
            url = feed_dict[source]
            
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                news = self._create_news_from_entry(entry, source)
                
                all_news.append(news)
        
        # Ordena as notícias por data de publicação (mais recentes primeiro)
        all_news.sort(key=lambda x: x.published_time)
        return all_news

    def _create_news_from_entry(self, entry: feedparser.FeedParserDict, source: str) -> News:
        """
        Cria um objeto News a partir de uma entrada do feed RSS.
        """
        # Obter a URL da imagem do feed
        image_url = None
        image_format = None
        
        if hasattr(entry, 'media_content') and entry.media_content:
            image_url = entry.media_content[0]['url']
            # Extrair o formato da imagem da URL
            image_format = image_url.split('.')[-1].lower()
        elif hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    image_url = link['href']
                    image_format = link['type'].split('/')[-1]
                    break
        
        # Se não encontrou imagem, usar a imagem padrão para a fonte
        if not image_url and source in DEFAULT_IMAGES:
            image_url = DEFAULT_IMAGES[source]['url']
            image_format = DEFAULT_IMAGES[source]['format']
        
        # Criar e retornar o objeto News
        return News(
            title=self.clean_html(entry.title),
            url=entry.link,
            source=source,
            published_time=self.convert_to_local_time(entry.published_parsed),
            summary=self.clean_html(entry.summary) if hasattr(entry, 'summary') else None,
            image_url=image_url,
            image_format=image_format
        )

    def get_unpublished_news(self, latest_news_by_source: Dict[str, str]) -> List[News]:
        """
        Filtra as notícias baseado no último horário de publicação por fonte.
        
        Args:
            latest_news_by_source: Dicionário com a fonte como chave e o último horário de publicação como valor
                                Ex: {"Cointelegraph": "2024-12-01 00:00", "Investing.com": "2024-12-01 00:00"}
        
        Returns:
            Lista de notícias mais recentes que o último horário registrado para cada fonte
        """
        # Se não houver dados no banco, retorna todas as notícias
        if not latest_news_by_source:
            return sorted(self.news, key=lambda x: x.published_time)
            
        filtered_news = []
        
        for news in self.news:
            latest_time = latest_news_by_source.get(news.source, "1970-01-01 00:00")
            
            # Compara o horário da notícia com o último horário registrado
            if news.published_time > latest_time:
                filtered_news.append(news)
    
        # Ordena as notícias por data de publicação (mais recentes primeiro)
        filtered_news.sort(key=lambda x: x.published_time)
        return filtered_news


rss_feeds = [
    {'Cointelegraph':'https://br.cointelegraph.com/rss'},
    {'Investing.com':'https://br.investing.com/rss/news_301.rss'}
]

def main():
    parser = FeedParser(rss_feeds)
    for news in parser.news:
        print("\nNotícia encontrada:")
        print(f"Título: {news.title}")
        print(f"URL: {news.url}")
        print(f"Fonte: {news.source}")
        print(f"Data de Publicação: {news.published_time}")
        if news.image_url:
            print(f"Imagem ({news.image_format}): {news.image_url}")
        if news.summary:
            print(f"Resumo: {news.summary}")
        print("-" * 80)

if __name__ == "__main__":
    main()