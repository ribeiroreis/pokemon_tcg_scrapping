# -*- coding: utf-8 -*-
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime

# Configurações do Chrome para rodar no GitHub Actions / headless
options = uc.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Iniciar o navegador Chrome com undetected_chromedriver
driver = uc.Chrome(options=options)

# Função para extrair dados da tabela após a interação
def get_table_data(driver, table_xpath):
    table = driver.find_element(By.XPATH, table_xpath)
    rows = table.find_elements(By.TAG_NAME, "tr")

    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        cols = [col.text for col in cols]
        data.append(cols)

    return data

# URL pública do Google Sheets em formato CSV
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSPXtRVhFqD8ADjOKjI3h-d81gmK0UdVTYfIKqe05N_QxvLxCiaEaua3bdv_oYX4c7fM606qG9dSHlz/pub?gid=464076543&single=true&output=csv'

# Carregar a planilha com cabeçalhos
sheet_data = pd.read_csv(spreadsheet_url)

# Acessar a coluna de URLs diretamente pelo nome da coluna 'url'
urls = sheet_data['url'].tolist()
colecoes = sheet_data.iloc[:, 0].tolist()

# Criar o DataFrame
data = []
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Iterar sobre as URLs e coleções
for colecao, url in zip(colecoes, urls):
    driver.get(url)

    try:
        close_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="lgpd-cookie"]/div/div[2]/button'))
        )
        close_button.click()
    except Exception as e:
        print("Pop-up não encontrado ou não pôde ser fechado:", e)

    # Clicar no botão para revelar a tabela
    button_xpath = '//*[@id="card-estoque"]/div[1]/div[2]/div/div[3]/div[1]/img'
    button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, button_xpath))
    )
    button.click()

    time.sleep(10)

    # Extrair dados da tabela
    table_xpath = '//*[@id="card-estoque"]/div[3]/div'
    table_data = get_table_data(driver, table_xpath)

    for row in table_data:
        data.append({'colecao': colecao, 'dados_tabela': row, 'extraction_time': current_time})

# Fechar o navegador
driver.quit()

# Criar DataFrame e salvar
df = pd.DataFrame(data)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f'raw/colecoes_{timestamp}.csv'
df.to_csv(output_path, index=False)

print(f'DataFrame salvo como {output_path}')
