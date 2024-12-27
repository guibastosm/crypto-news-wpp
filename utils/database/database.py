from supabase import create_client
from dotenv import load_dotenv
import os
from typing import List, Optional, Dict
from utils.rss.feed_parser import News

class Database:
    def __init__(self):
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Configurar cliente Supabase
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
        
        self.client = create_client(url, key)
        self.table_name = "crypto-news"  # Nome da tabela no Supabase

    def insert_news(self, news: News) -> Dict:
        """
        Insere uma nova notícia no banco de dados.
        Retorna os dados inseridos.
        """
        data = {
            "title": news.title,
            "url": news.url,
            "source": news.source,
            "published_time": news.published_time,
            "summary": news.summary,
            "image_url": news.image_url,
            "image_format": news.image_format
        }
        
        result = self.client.table(self.table_name).insert(data).execute()
        return result.data

    def insert_many_news(self, news_list: List[News]) -> List[Dict]:
        """
        Insere várias notícias no banco de dados.
        Retorna a lista de dados inseridos.
        """
        data = [{
            "title": news.title,
            "url": news.url,
            "source": news.source,
            "published_time": news.published_time,
            "summary": news.summary,
            "image_url": news.image_url,
            "image_format": news.image_format
        } for news in news_list]
        
        result = self.client.table(self.table_name).insert(data).execute()
        return result.data

    def get_latest_news_per_source(self) -> Dict[str, str]:
        """
        Retorna as últimas notícias por fonte usando a stored procedure get_latest_news_per_source.
        Retorna um dicionário no formato {"source1": "time1", "source2": "time2", ...}
        """
        result = self.client.rpc('get_latest_news_per_source').execute()
        data = result.data
    
        # Formatar os dados no formato de dicionário
        return {item['source']: item['published_time'] for item in data}


if __name__ == "__main__":
    db = Database()
    print(db.get_latest_news_per_source())