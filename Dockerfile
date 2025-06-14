
FROM python:3.11-slim

RUN apt-get update && apt-get install -y wget gnupg2 unzip     && rm -rf /var/lib/apt/lists/*

# Instalação do Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -     && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list     && apt-get update && apt-get install -y google-chrome-stable

# Instalação do chromedriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP "\d+\.\d+\.\d+") &&     CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) &&     wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip &&     unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ &&     rm /tmp/chromedriver.zip

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
