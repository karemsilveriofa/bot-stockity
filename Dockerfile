# Use imagem oficial do Selenium com Chrome já configurado
FROM selenium/standalone-chrome:114.0

USER root

# Atualiza e instala python3 e pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /usr/src/app

# Copia arquivos do projeto
COPY requirements.txt main.py ./

# Instala dependências python
RUN pip3 install --no-cache-dir -r requirements.txt

# Comando para rodar o bot
CMD ["python3", "main.py"]
