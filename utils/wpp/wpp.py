import requests
from typing import Optional
import os
from dotenv import load_dotenv
import io
from utils.rss.feed_parser import News

class WhatsAppSender:
    def __init__(self):
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Configurar endpoint e ID da newsletter
        self.base_url = "http://localhost:3000"
        self.newsletter_id = os.getenv("NEWSLETTER_ID")
        if not self.newsletter_id:
            raise ValueError("NEWSLETTER_ID deve estar definida no arquivo .env")
            
        self.session = requests.Session()
        
    def send_news(self, news: News, image_bytes: bytes) -> bool:
        """
        Envia uma notícia com imagem para a newsletter do WhatsApp.
        
        Args:
            news: Objeto News contendo as informações da notícia
            image_bytes: Bytes da imagem a ser enviada
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        try:
            # Preparar a mensagem
            caption = f"*{news.title}*\n\n"
            if news.summary:
                caption += f"{news.summary}\n\n"
            caption += f"Fonte: {news.source}\n"
            caption += f"Leia mais: {news.url}"
            
            # Criar arquivo temporário em memória
            image_io = io.BytesIO(image_bytes)
            image_io.name = f"news_image.{news.image_format}"
            
            # Preparar os dados do formulário
            files = {
                'image': ('image.' + news.image_format, image_io, 'image/' + news.image_format)
            }
            
            data = {
                'phone': f"{self.newsletter_id}@newsletter",
                'caption': caption,
                'view_once': 'false',
                'compress': 'false'
            }
            
            # Enviar a requisição
            response = self.session.post(
                f"{self.base_url}/send/image",
                files=files,
                data=data,
                timeout=30
            )
            
            response.raise_for_status()
            return True
            
        except requests.RequestException as e:
            print(f"Erro ao enviar mensagem para WhatsApp: {str(e)}")
            return False


if __name__ == "__main__":
    # Teste do envio de mensagem
    from utils.scraper.scraper import ImageScraper
    
    # Criar uma notícia de teste
    news = News(
        title="Bitcoin atinge nova máxima histórica!",
        url="https://example.com",
        source="Cointelegraph",
        published_time="2023-01-01 00:00:00",
        summary="O Bitcoin atingiu um novo recorde histórico hoje...",
        image_url="https://images.cointelegraph.com/images/840_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBoLmNvbS91cGxvYWRzLzIwMjQtMTIvMDE5M2U0MzItOTg2YS03NmZmLTlmZWYtZjEzNTJhM2Q2NjE4.jpg",
        image_format="jpeg"
    )
    
    # Baixar a imagem
    scraper = ImageScraper()
    image_bytes, _ = scraper.get_image_bytes(news)
    
    if image_bytes:
        # Enviar a mensagem
        sender = WhatsAppSender()
        success = sender.send_news(news, image_bytes)
        print(f"Mensagem enviada com sucesso: {success}")
    else:
        print("Erro ao baixar a imagem")
