FROM python:3.9-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    chromium \
    chromium-driver \
    xvfb \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root
RUN groupadd -r chrome && useradd -r -g chrome -G audio,video chrome \
    && mkdir -p /home/chrome && chown -R chrome:chrome /home/chrome

WORKDIR /app

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cria script de entrypoint
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Inicia o Xvfb\n\
echo "Iniciando Xvfb..."\n\
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &\n\
export DISPLAY=:99\n\
\n\
# Aguarda o Xvfb iniciar\n\
echo "Aguardando Xvfb..."\n\
sleep 1\n\
\n\
# Define variáveis de ambiente para o Chrome\n\
export CHROME_BIN=/usr/bin/chromium\n\
export CHROMEDRIVER_PATH=/usr/bin/chromedriver\n\
\n\
# Executa o comando passado\n\
echo "Executando comando: $@"\n\
exec "$@"' > /app/entrypoint.sh

# Define permissões antes de mudar o dono
RUN chmod +x /app/entrypoint.sh

# Copia o código da aplicação
COPY . .

# Ajusta permissões finais
RUN chown -R chrome:chrome /app

# Usa dumb-init como entrypoint para melhor gestão de processos
ENTRYPOINT ["dumb-init", "--", "/app/entrypoint.sh"]

# Define o usuário não-root
USER chrome

# Comando padrão
CMD ["python", "-u", "main.py"]
