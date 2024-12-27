import feedparser
from typing import List, Dict

class FeedHandler:
    def __init__(self):
        self.feed_urls = [
            'https://cointelegraph.com/rss',
            'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'https://cryptonews.com/news/feed'
        ]

    def get_feeds(self) -> List[Dict]:
        all_news = []
        
        for url in self.feed_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    news_item = {
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.published,
                        'summary': entry.summary,
                        'source': url
                    }
                    all_news.append(news_item)
            except Exception as e:
                print(f"Error fetching feed from {url}: {str(e)}")
                
        return all_news
