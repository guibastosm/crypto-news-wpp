import base64
from typing import Optional, Tuple
from utils.rss.feed_parser import News
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import random
import os
import subprocess
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageScraper:
    def __init__(self):
        self._setup_driver()
        
    def _get_chromedriver_path(self):
        """
        Tenta localizar o ChromeDriver no sistema ou usa o path do Docker
        """
        logger.info("Procurando ChromeDriver...")
        
        # Primeiro verifica se está no ambiente Docker
        if os.environ.get('CHROMEDRIVER_PATH'):
            path = os.environ['CHROMEDRIVER_PATH']
            logger.info(f"Usando ChromeDriver do ambiente: {path}")
            return path
            
        # Depois tenta usar o which para encontrar o chromedriver
        try:
            chromedriver_path = subprocess.check_output(['which', 'chromedriver']).decode().strip()
            if chromedriver_path:
                logger.info(f"ChromeDriver encontrado via 'which': {chromedriver_path}")
                return chromedriver_path
        except Exception as e:
            logger.warning(f"Erro ao procurar ChromeDriver via 'which': {str(e)}")
        
        # Caminhos comuns do ChromeDriver no Ubuntu
        possible_paths = [
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver',
            '/snap/bin/chromedriver',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"ChromeDriver encontrado em: {path}")
                return path
                
        logger.warning("Usando 'chromedriver' do PATH como última opção")
        return 'chromedriver'
        
    def _setup_driver(self):
        """
        Configura o driver do Chrome em modo headless
        """
        logger.info("Configurando Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        
        # Define o binário do Chrome se estiver no Docker
        if os.environ.get('CHROME_BIN'):
            binary_location = os.environ['CHROME_BIN']
            logger.info(f"Usando binário do Chrome: {binary_location}")
            chrome_options.binary_location = binary_location
        
        # Adiciona user agent aleatório
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        user_agent = random.choice(user_agents)
        chrome_options.add_argument(f'user-agent={user_agent}')
        logger.info(f"User Agent selecionado: {user_agent}")
        
        try:
            # Verifica variáveis de ambiente importantes
            logger.info(f"DISPLAY: {os.environ.get('DISPLAY', 'não definido')}")
            logger.info(f"HOME: {os.environ.get('HOME', 'não definido')}")
            
            # Tenta encontrar o ChromeDriver no sistema
            chromedriver_path = self._get_chromedriver_path()
            logger.info(f"Usando ChromeDriver em: {chromedriver_path}")
            
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("Chrome driver inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar o Chrome driver: {str(e)}", exc_info=True)
            raise
            
    def __del__(self):
        """
        Garante que o driver seja fechado quando o objeto for destruído
        """
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass
                
    def get_image_bytes(self, news: News) -> Optional[Tuple[bytes, str]]:
        """
        Baixa a imagem da notícia usando Selenium e retorna os bytes e o formato.
        
        Args:
            news: Objeto News contendo a URL da imagem
            
        Returns:
            Tupla contendo os bytes da imagem e o formato, ou None se falhar
        """
        if not news.image_url:
            return None
            
        try:
            # Adiciona um pequeno delay aleatório
            time.sleep(random.uniform(1, 3))
            
            # Navega até a URL da imagem
            self.driver.get(news.image_url)
            
            # Executa script JavaScript para pegar a imagem em base64
            script = """
                let img = document.querySelector('img');
                if (!img) {
                    img = document.body.querySelector('*');  // pega qualquer elemento se não encontrar img
                }
                let canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth || img.width;
                canvas.height = img.naturalHeight || img.height;
                let ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                return canvas.toDataURL('image/jpeg');
            """
            
            # Espera um pouco para a imagem carregar
            time.sleep(2)
            
            # Executa o script e obtém os dados da imagem
            img_base64 = self.driver.execute_script(script)
            
            if img_base64 and ',' in img_base64:
                # Remove o prefixo do data URL e decodifica
                img_data = base64.b64decode(img_base64.split(',')[1])
                return img_data, news.image_format
                
        except TimeoutException:
            logger.warning(f"Timeout ao tentar carregar a imagem: {news.image_url}")
        except WebDriverException as e:
            logger.error(f"Erro do WebDriver ao baixar imagem da URL {news.image_url}: {str(e)}")
        except Exception as e:
            logger.error(f"Erro inesperado ao baixar imagem da URL {news.image_url}: {str(e)}")
            
        # Se falhar, tenta reiniciar o driver
        try:
            self.driver.quit()
            self._setup_driver()
        except:
            pass
            
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
    
    logger.info("Baixando imagem...")
    image_bytes, image_format = scraper.get_image_bytes(news)
    
    if image_bytes:
        # Salva a imagem em dois arquivos diferentes para teste
        with open("test_image.jpg", "wb") as f:
            f.write(image_bytes)
        logger.info(f"Imagem salva como 'test_image.jpg'")
        logger.info(f"Formato da imagem: {image_format}")
    else:
        logger.warning("Falha ao baixar a imagem")