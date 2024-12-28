import requests
from typing import Optional, Dict, Tuple
import io
from utils.rss.feed_parser import News
from dotenv import load_dotenv
import os

class ImageScraper:
    def __init__(self):
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Configurar ZenRows API
        self.api_key = os.getenv("ZENROWS_API_KEY")
        if not self.api_key:
            raise ValueError("ZENROWS_API_KEY deve estar definida no arquivo .env")
            
        self.session = requests.Session()
        self.zenrows_url = "https://api.zenrows.com/v1/"
        
    def get_image_bytes(self, news: News) -> Optional[Tuple[bytes, str]]:
        """
        Baixa a imagem da notícia usando ZenRows API e retorna os bytes e o formato.
        
        Args:
            news: Objeto News contendo a URL da imagem
            
        Returns:
            Tupla contendo os bytes da imagem e o formato, ou None se falhar
        """
        if not news.image_url:
            return None
            
        try:
            # Parâmetros para a API ZenRows
            params = {
                'url': news.image_url,
                'apikey': self.api_key,
            }
            
            # Fazer o download da imagem através do ZenRows
            response = self.session.get(self.zenrows_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Retornar os bytes da imagem e o formato
            return response.content, news.image_format
            
        except requests.RequestException as e:
            print(f"Erro ao baixar imagem da URL {news.image_url}: {str(e)}")
            return None


if __name__ == "__main__":
    scraper = ImageScraper()
    news = News(
        title="Teste",
        url="https://example.com",
        source="Teste",
        published_time="2023-01-01 00:00:00",
        summary="Teste",
        image_url="https://images.cointelegraph.com/images/840_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBoLmNvbS91cGxvYWRzLzIwMjQtMTIvMDE5M2U0MzItOTg2YS03NmZmLTlmZWYtZjEzNTJhM2Q2NjE4.jpg",
        image_format="jpeg"
    )
    image_bytes, image_format = scraper.get_image_bytes(news)
    
    if image_bytes:
        with open("image.jpg", "wb") as f:
            f.write(image_bytes)
        
        print(f"Formato da imagem: {image_format}")