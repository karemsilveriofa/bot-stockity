FROM selenium/standalone-chrome:114.0

# Instala o Python
USER root
RUN apt-get update && apt-get install -y python3-pip

# Define o diretório de trabalho
WORKDIR /usr/src/app

# Copia o requirements.txt e o main.py
COPY requirements.txt main.py ./

# Instala as dependências do Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Executa o bot
CMD ["python3", "main.py"]
