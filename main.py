import time
from utils.rss.feed_parser import FeedParser, rss_feeds
from utils.scraper.scraper import ImageScraper
from utils.wpp.wpp import WhatsAppSender
from utils.database.database import Database

def main():
    feed = FeedParser(rss_feeds)
    db = Database()
    latest_news_times_by_source = db.get_latest_news_per_source()    
    unpublished_news = feed.get_unpublished_news(latest_news_times_by_source)
    
    if not unpublished_news:
        print("Nenhuma notícia nova encontrada")
        return
        
    print(f"Encontradas {len(unpublished_news)} notícias novas")
    
    # Inserir novas notícias no banco
    db.insert_many_news(unpublished_news)
    print("Notícias inseridas no banco de dados")
    
    # Enviar notícias para o WhatsApp
    wpp = WhatsAppSender()
    scraper = ImageScraper()
    
    for news in unpublished_news:
        print(f"\nProcessando notícia: {news.title}")
        # Baixar imagem
        image_bytes, image_format = scraper.get_image_bytes(news)
        if not image_bytes:
            print(f"Erro ao baixar a imagem para {news.image_url}")
            continue
            
        # Enviar mensagem
        success = wpp.send_news(news, image_bytes)
        if success:
            print(f"Mensagem enviada com sucesso para {news.source}")
        else:
            print(f"Erro ao enviar noticia {news.source} link:{news.url} ")
            
        time.sleep(2)


if __name__ == "__main__":
    main()
