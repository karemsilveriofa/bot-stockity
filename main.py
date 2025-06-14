
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests

# Configurações do Telegram
TELEGRAM_TOKEN = "7239698274:AAFyg7HWLPvXceJYDope17DkfJpxtU4IU2Y"
CHAT_ID = "6821521589"

# URLs e ativos
URL = "https://stockity.id/trading"
ATIVOS = ["Altcoin IDX", "Cripto IDX"]

# Função para enviar mensagem no telegram
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Erro ao enviar mensagem Telegram: {e}")

# Função para extrair dados das velas (simplificado)
def pegar_dados_ativos(driver):
    dados = {}
    for ativo in ATIVOS:
        try:
            # Procurar pelo painel do ativo
            painel = driver.find_element(By.XPATH, f'//div[contains(text(),"{ativo}")]/ancestor::div[contains(@class,"card")]')
            # Aqui você ajustaria o seletor correto para pegar o preço ou vela
            # Exemplo fictício (ajustar conforme HTML da página):
            velas = painel.find_elements(By.CSS_SELECTOR, ".candle") # exemplo fictício
            # Pegar últimos preços de fechamento (simulação)
            if len(velas) >= 2:
                fechamento_ultimo = float(velas[-1].get_attribute("data-close"))
                fechamento_anterior = float(velas[-2].get_attribute("data-close"))
                dados[ativo] = (fechamento_anterior, fechamento_ultimo)
            else:
                dados[ativo] = None
        except Exception as e:
            dados[ativo] = None
            print(f"Erro ao pegar dados de {ativo}: {e}")
    return dados

# Função simples para definir sinal compra ou venda
def analisar_sinal(fechamento_anterior, fechamento_ultimo):
    if fechamento_ultimo > fechamento_anterior:
        return "COMPRA"
    else:
        return "VENDA"

def main():
    # Configurar Selenium para rodar headless
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    time.sleep(15)  # esperar a página carregar e autenticar se necessário

    print("Bot iniciado e acessando Stockity...")

    while True:
        try:
            now = datetime.utcnow() + timedelta(hours=-3)  # Ajuste para horário Brasília (-3h UTC)
            seg_ate_minuto = 60 - now.second

            # Esperar até 5 segundos antes da próxima vela começar
            if seg_ate_minuto > 5:
                time.sleep(seg_ate_minuto - 5)
            else:
                time.sleep(seg_ate_minuto + 55)  # caso tenha passado dos 5 seg

            # Atualizar dados ativos
            driver.refresh()
            time.sleep(10)  # esperar atualizar

            dados = pegar_dados_ativos(driver)
            sinais = {}
            for ativo, valores in dados.items():
                if valores is not None:
                    fechamento_anterior, fechamento_ultimo = valores
                    sinal = analisar_sinal(fechamento_anterior, fechamento_ultimo)
                    sinais[ativo] = sinal
                else:
                    sinais[ativo] = None

            # Escolher o ativo com sinal mais "forte" (simples, aqui escolhemos o ativo que teve maior diferença)
            ativo_selecionado = None
            maior_dif = 0
            for ativo, valores in dados.items():
                if valores is not None:
                    diff = abs(valores[1] - valores[0])
                    if diff > maior_dif:
                        maior_dif = diff
                        ativo_selecionado = ativo

            if ativo_selecionado and sinais[ativo_selecionado]:
                horario_operacao = (datetime.utcnow() + timedelta(hours=-3) + timedelta(minutes=1)).strftime("%H:%M")
                mensagem = f"Sinal para {ativo_selecionado}: {sinais[ativo_selecionado]} às {horario_operacao}"
                print(mensagem)
                send_telegram_message(mensagem)
            else:
                print("Sem dados suficientes para sinal.")

        except Exception as e:
            print(f"Erro no loop principal: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
