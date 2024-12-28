# Crypto News Scraper

Um bot que monitora e envia notícias sobre criptomoedas via WhatsApp.

## Funcionalidades

- Coleta notícias de fontes confiáveis (Cointelegraph, Investing.com)
- Armazena histórico de notícias no Supabase
- Envia notícias via WhatsApp com imagens
- Evita duplicatas de notícias
- Roda em container Docker

## Configuração

1. Clone o repositório
```bash
git clone [URL_DO_SEU_REPOSITORIO]
cd crypto-news-scraper
```

2. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

3. Rode com Docker
```bash
# Construa a imagem
docker build -t crypto-news-scraper .

# Execute o container
docker run --env-file .env crypto-news-scraper
```

## Variáveis de Ambiente

- `SUPABASE_URL`: URL do seu projeto Supabase
- `SUPABASE_KEY`: Chave de API do Supabase
- `ZENROWS_API_KEY`: Chave de API do ZenRows para scraping
- `NEWSLETTER_ID`: ID do grupo/chat do WhatsApp

## Tecnologias

- Python 3.9
- Supabase (banco de dados)
- Docker
- RSS Feed Parser
- ZenRows (web scraping)
