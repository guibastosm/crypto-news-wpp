import feedparser
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
from datetime import datetime, timedelta
import time

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

    def clean_html(self, html_text: str) -> str:
        """Remove tags HTML e retorna apenas o texto."""
        # Remove tags de imagem completas
        text = re.sub(r'<p[^>]*>(?:\s*<img[^>]*>\s*)*</p>', '', html_text)
        # Remove todas as outras tags HTML
        text = re.sub(r'<[^>]+>', '', text)
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

    def parse_feeds(self) -> List[News]:
        all_news = []
        
        for feed_dict in self.rss_feeds:
            source = list(feed_dict.keys())[0]
            url = feed_dict[source]
            
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                # Extrair URL da imagem se disponível
                image_url = None
                if hasattr(entry, 'media_content'):
                    for media in entry.media_content:
                        if media.get('url', '').lower().endswith(('.jpg', '.png')):
                            image_url = media['url']
                            break
                elif hasattr(entry, 'links'):
                    for link in entry.links:
                        if link.get('type', '').startswith('image/') and link.get('href', '').lower().endswith(('.jpg', '.png')):
                            image_url = link['href']
                            break

                # Extrair formato da imagem
                image_format = None
                if image_url:
                    if image_url.lower().endswith('.jpg'):
                        image_format = 'jpg'
                    elif image_url.lower().endswith('.png'):
                        image_format = 'png'

                # Extrair e limpar o summary
                summary = None
                if hasattr(entry, 'summary'):
                    summary = self.clean_html(entry.summary)

                # Converter o tempo de publicação para o formato correto
                published_time = self.convert_to_local_time(entry.published_parsed)
                
                news = News(
                    title=entry.title,
                    url=entry.link,
                    source=source,
                    published_time=published_time,
                    summary=summary,
                    image_url=image_url,
                    image_format=image_format
                )
                
                all_news.append(news)
                all_news.sort(key=lambda x: x.published_time)
        
        return all_news

rss_feeds = [
    {'Cointelegraph':'https://cointelegraph.com/rss'},
    {'Intesting.com':'https://br.investing.com/rss/news_301.rss'}
]

def main():
    parser = FeedParser(rss_feeds)
    news_list = parser.parse_feeds()
    for news in news_list:
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