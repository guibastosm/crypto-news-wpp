import feedparser
from typing import List, Dict, Optional
import re

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

    def parse_feeds(self) -> List[Dict]:
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
                    print(summary)

                news_item = {
                    'title': entry.title,
                    'url': entry.link,
                    'image_url': image_url,
                    'image_format': image_format,
                    'source': source,
                    'summary': summary
                }
                
                all_news.append(news_item)
        
        return all_news

rss_feeds = [
    {'Cointelegraph':'https://cointelegraph.com/rss'},
    {'Intesting.com':'https://br.investing.com/rss/news_301.rss'}
]

def main():
    parser = FeedParser(rss_feeds)
    news = parser.parse_feeds()
    for item in news:
        print("\nNotícia encontrada:")
        print(f"Título: {item['title']}")
        print(f"URL: {item['url']}")
        print(f"Fonte: {item['source']}")
        if item['image_url']:
            print(f"Imagem ({item['image_format']}): {item['image_url']}")
        print(f"Resumo: {item['summary']}")
        print("-" * 80)

if __name__ == "__main__":
    main()