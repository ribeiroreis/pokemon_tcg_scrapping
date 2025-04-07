import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import os

# Iniciar o navegador Chrome com webdriver-manager
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # importante para rodar no GitHub Actions
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL pública do Google Sheets em formato CSV
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSPXtRVhFqD8ADjOKjI3h-d81gmK0UdVTYfIKqe05N_QxvLxCiaEaua3bdv_oYX4c7fM606qG9dSHlz/pub?gid=464076543&single=true&output=csv'

# Carregar a planilha com cabeçalhos
sheet_data = pd.read_csv(spreadsheet_url)
urls = sheet_data['url'].tolist()
colecoes = sheet_data.iloc[:, 0].tolist()

# Função para extrair dados da tabela
def get_table_data(driver, table_xpath):
    table = driver.find_element(By.XPATH, table_xpath)
    rows = table.find_elements(By.TAG_NAME, "tr")
    return [[col.text for col in row.find_elements(By.TAG_NAME, "td")] for row in rows]

data = []
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for colecao, url in zip(colecoes, urls):
    driver.get(url)
    time.sleep(2)
    try:
        button_xpath = '//*[@id="card-estoque"]/div[1]/div[2]/div/div[3]/div[1]/img'
        driver.find_element(By.XPATH, button_xpath).click()
        time.sleep(3)
        table_xpath = '//*[@id="card-estoque"]/div[3]/div'
        table_data = get_table_data(driver, table_xpath)
        for row in table_data:
            data.append({'colecao': colecao, 'dados_tabela': row, 'extraction_time': current_time})
    except Exception as e:
        print(f"Erro ao processar {colecao}: {e}")

driver.quit()

df = pd.DataFrame(data)
print(df)

# Exportar para pasta raw do repositório
os.makedirs('raw', exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f'raw/colecoes_{timestamp}.csv'
df.to_csv(output_path, index=False)
