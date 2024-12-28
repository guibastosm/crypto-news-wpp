# Use uma imagem base Python oficial
FROM python:3.9-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código fonte para o container
COPY . .

# Define a variável de ambiente para Python não criar arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Define a variável de ambiente para Python não bufferizar a saída
ENV PYTHONUNBUFFERED 1

# Comando para rodar o script
CMD ["python", "main.py"]
