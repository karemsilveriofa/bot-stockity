import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
import statistics

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise Exception("Informe TELEGRAM_TOKEN e CHAT_ID nas variáveis de ambiente")

URL = "https://stockity.id/trading"
ATIVOS = ["Altcoin IDX", "Cripto IDX"]

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Erro ao enviar mensagem Telegram: {e}")

def pegar_dados_ativos(driver):
    dados = {}
    for ativo in ATIVOS:
        try:
            painel = driver.find_element(By.XPATH, f'//div[contains(text(),"{ativo}")]/ancestor::div[contains(@class,"card")]')
            velas = painel.find_elements(By.CSS_SELECTOR, ".candle")  # Seletor de velas
            fechamentos = []
            for v in velas[-5:]:
                close = v.get_attribute("data-close")
                if close:
                    fechamentos.append(float(close))
            if len(fechamentos) < 5:
                dados[ativo] = None
            else:
                dados[ativo] = fechamentos
        except Exception as e:
            print(f"Erro ao pegar dados de {ativo}: {e}")
            dados[ativo] = None
    return dados

def analisar_sinal(fechamentos):
    ultimos_3 = fechamentos[-3:]
    anteriores_2 = fechamentos[-5:-3]
    media_ultimos_3 = statistics.mean(ultimos_3)
    media_anteriores_2 = statistics.mean(anteriores_2)
    volatilidade = statistics.stdev(fechamentos)

    VOLATILIDADE_MIN = 0.0005

    if volatilidade < VOLATILIDADE_MIN:
        return None

    if media_ultimos_3 > media_anteriores_2:
        return "COMPRA"
    elif media_ultimos_3 < media_anteriores_2:
        return "VENDA"
    else:
        return None

def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    time.sleep(15)  # espera a página carregar
    
    print("Bot iniciado e acessando Stockity...")

    ultimo_envio = datetime.min

    while True:
        try:
            agora = datetime.utcnow() + timedelta(hours=-3)  # horário de Brasília
            segundos_ate_minuto = 60 - agora.second

            if segundos_ate_minuto > 5:
                time.sleep(segundos_ate_minuto - 5)
            else:
                time.sleep(segundos_ate_minuto + 55)

            agora = datetime.utcnow() + timedelta(hours=-3)
            minuto_corrente = agora.replace(second=0, microsecond=0)

            if (agora - ultimo_envio).total_seconds() < 120:
                continue

            driver.refresh()
            time.sleep(10)

            dados = pegar_dados_ativos(driver)
            sinais = {}
            for ativo, fechamentos in dados.items():
                if fechamentos:
                    sinal = analisar_sinal(fechamentos)
                    sinais[ativo] = sinal
                else:
                    sinais[ativo] = None

            ativo_selecionado = None
            maior_volatilidade = 0
            for ativo, fechamentos in dados.items():
                if fechamentos and sinais[ativo]:
                    vol = statistics.stdev(fechamentos)
                    if vol > maior_volatilidade:
                        maior_volatilidade = vol
                        ativo_selecionado = ativo

            if ativo_selecionado and sinais[ativo_selecionado]:
                horario_operacao = (minuto_corrente + timedelta(minutes=1)).strftime("%H:%M")
                mensagem = f"Sinal para {ativo_selecionado}: {sinais[ativo_selecionado]} às {horario_operacao}"
                print(mensagem)
                send_telegram_message(mensagem)
                ultimo_envio = agora
            else:
                print(f"{agora.strftime('%H:%M:%S')} - Sem sinal confiável.")

        except Exception as e:
            print(f"Erro no loop principal: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
    
