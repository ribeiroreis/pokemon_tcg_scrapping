import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Fun��o para extrair dados da tabela ap�s a intera��o
def get_table_data(driver, table_xpath):
    table = driver.find_element(By.XPATH, table_xpath)
    rows = table.find_elements(By.TAG_NAME, "tr")

    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        cols = [col.text for col in cols]  # Obter o texto de cada coluna
        data.append(cols)

    return data

# Iniciar o navegador Chrome
driver = webdriver.Chrome(options=chrome_options)

# URL p�blica do Google Sheets em formato CSV
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSPXtRVhFqD8ADjOKjI3h-d81gmK0UdVTYfIKqe05N_QxvLxCiaEaua3bdv_oYX4c7fM606qG9dSHlz/pub?gid=464076543&single=true&output=csv'

# Carregar a planilha com cabe�alhos
sheet_data = pd.read_csv(spreadsheet_url)

# Acessar a coluna de URLs diretamente pelo nome da coluna 'url'
urls = sheet_data['url'].tolist()  # Usar o nome correto da coluna 'url'

# Obter a coluna A (cole��o)
colecoes = sheet_data.iloc[:, 0].tolist()  # Pegar todos os valores da primeira coluna (A)

# Criar o DataFrame
data = []
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Capturar a data e hora atuais

# Iterar sobre as URLs e cole��es ao mesmo tempo
for colecao, url in zip(colecoes, urls):
    driver.get(url)  # Acessar a URL

    # Tentar fechar o pop-up de cookies, se existir
    try:
        # Suponha que o bot�o de fechar tenha um ID espec�fico (substitua 'close-button-id' conforme necess�rio)
        close_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="lgpd-cookie"]/div/div[2]/button'))  # Altere o ID conforme necess�rio
        )
        close_button.click()
    except Exception as e:
        print("Pop-up n�o encontrado ou n�o p�de ser fechado:", e)

    # Localizar e clicar no bot�o pelo XPath
    button_xpath = '//*[@id="card-estoque"]/div[1]/div[2]/div/div[3]/div[1]/img'
    button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, button_xpath))
    )
    button.click()

    # Aguardar um momento para a p�gina carregar ap�s o clique
    time.sleep(10)

    # Extrair dados da tabela usando o XPath
    table_xpath = '//*[@id="card-estoque"]/div[3]/div'
    table_data = get_table_data(driver, table_xpath)

    # Adicionar dados ao DataFrame com a coluna 'colecao'
    for row in table_data:
        data.append({'colecao': colecao, 'dados_tabela': row, 'extraction_time': current_time})

# Fechar o navegador
driver.quit()

# Criar o DataFrame final com os dados extra�dos
df = pd.DataFrame(data)

# Criar nome do arquivo com 'colecoes' + data e hora atuais
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f'colecoes_{timestamp}.csv'  # Salvar no diret�rio atual do Replit

# Salvar o DataFrame em um arquivo CSV no diret�rio especificado
df.to_csv(output_path, index=False)

print(f'DataFrame salvo como {output_path}')
