
# Usa a imagem oficial do Python como imagem base
FROM python:3.10.12

# Define o diretório de trabalho no contêiner
WORKDIR /app


# Copia os arquivos do projeto para o diretório de trabalho no contêiner
COPY . .

# Instala as dependências Python listadas no arquivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt



# Expose a porta que a aplicação irá rodar
EXPOSE 8080

# Dá permissão de execução ao script
RUN chmod +x /app/start.sh

# Define o script shell como o ponto de entrada do contêiner
ENTRYPOINT ["/app/start.sh"]







