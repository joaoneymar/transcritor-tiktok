# Usa uma versão leve do Python
FROM python:3.11-slim

# Instala o FFmpeg (O segredo para não dar erro!)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Cria a pasta do app
WORKDIR /app

# Copia os arquivos do seu projeto
COPY . .

# Instala as bibliotecas do Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para iniciar o site
CMD ["python", "main.py"]
