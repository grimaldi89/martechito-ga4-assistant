# Use uma imagem base oficial do Python
FROM python:3.9-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação para o diretório de trabalho
COPY . .

# Defina a variável de ambiente para o Flask
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0

# Exponha a porta em que o Flask vai rodar
EXPOSE 5000

# Comando para rodar o servidor Flask
CMD ["flask", "run"]