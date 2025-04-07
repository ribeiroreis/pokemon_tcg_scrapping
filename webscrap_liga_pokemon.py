import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import os

# Iniciar o navegador Chrome com opções para CI
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # headless compatível com layout moderno
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL pública do Google Sheets em formato CSV
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSPXtRVhFqD8ADjOKjI3h-d81gmK0UdVTYfIKqe05N_QxvLxCiaEaua3bdv_oYX4c7fM606qG9dSHlz/pub?gid=464076543&single=true&output=csv'

# Carregar a planilha
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
    try:
        # Espera até o botão de expandir estoque aparecer
        button_xpath = '//*[@id="card-estoque"]/div[1]/div[2]/div/div[3]/div[1]/img'
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        ).click()

        # Espera até a tabela aparecer
        table_xpath = '//*[@id="card-estoque"]/div[3]/div'
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, table_xpath))
        )

        table_data = get_table_data(driver, table_xpath)
        for row in table_data:
            data.append({'colecao': colecao, 'dados_tabela': row, 'extraction_time': current_time})
    except Exception as e:
        print(f"Erro ao processar {colecao}: {e}")
        # Salvar screenshot pra debug
        screenshot_path = f'screenshot_{colecao.replace(" ", "_")}.png'
        driver.save_screenshot(screenshot_path)

driver.quit()

# Salvar dados como CSV
df = pd.DataFrame(data)
print(df)

os.makedirs('raw', exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f'raw/colecoes_{timestamp}.csv'
df.to_csv(output_path, index=False)
