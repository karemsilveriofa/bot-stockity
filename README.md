
# Bot de Sinais Stockity IDX

Este bot acessa a plataforma Stockity (https://stockity.id/trading), monitora os ativos Altcoin IDX e Cripto IDX, analisa as velas de 1 minuto e envia sinais de COMPRA ou VENDA para um bot Telegram.

## Configuração

1. Atualize o arquivo `main.py` com seu TOKEN do Telegram e CHAT_ID.
2. Configure o deploy na Render usando o Dockerfile fornecido.
3. O bot roda em headless Chrome, acessando a página, pegando os dados e enviando sinais a cada minuto, sincronizado para enviar 5 segundos antes da nova vela.

## Como rodar localmente

- Instale o Chrome e chromedriver
- Instale dependências com `pip install -r requirements.txt`
- Execute `python main.py`

## Observações

- A análise é simples e pode ser aprimorada.
- Os seletores para pegar as velas devem ser ajustados conforme o HTML do site Stockity.
- O bot precisa de acesso à internet e permissão para abrir navegador.
