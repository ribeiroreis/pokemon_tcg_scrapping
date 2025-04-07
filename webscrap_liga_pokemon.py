import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from datetime import datetime
import os

# Função para medir o tempo de execução
start_time = time.time()

# Função para extrair dados da tabela após a interação
def get_table_data(driver, table_xpath):
    try:
        table = driver.find_element(By.XPATH, table_xpath)
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            cols = [col.text for col in cols]
            data.append(cols)
        return data
    except NoSuchElementException:
        print("⚠️ Tabela não encontrada.")
        return []

# Iniciar o navegador Chrome (modo visível)
driver = webdriver.Chrome()

# Carregar dados da planilha
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSPXtRVhFqD8ADjOKjI3h-d81gmK0UdVTYfIKqe05N_QxvLxCiaEaua3bdv_oYX4c7fM606qG9dSHlz/pub?gid=464076543&single=true&output=csv'
sheet_data = pd.read_csv(spreadsheet_url)

# Colunas: coleção e URLs
colecoes = sheet_data.iloc[:, 0].tolist()
urls = sheet_data['url'].tolist()

# Lista para armazenar os dados extraídos
data = []
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Loop principal
for colecao, url in zip(colecoes, urls):
    print(f"Acessando coleção: {colecao} - {url}")
    driver.get(url)

    # Clicar no botão para abrir a tabela
    try:
        button_xpath = '//*[@id="card-estoque"]/div[1]/div[2]/div/div[3]/div[1]/img'
        driver.find_element(By.XPATH, button_xpath).click()
    except (NoSuchElementException, TimeoutException):
        print("⚠️ Botão não encontrado.")
        continue

    # Espera para garantir que a tabela carregue
    time.sleep(5)

    # Extrair dados da tabela
    table_xpath = '//*[@id="card-estoque"]/div[3]/div'
    table_data = get_table_data(driver, table_xpath)

    # Adicionar dados ao dataset
    for row in table_data:
        data.append({'colecao': colecao, 'dados_tabela': row, 'extraction_time': current_time})

# Fechar o navegador
driver.quit()

# Criar DataFrame final
df = pd.DataFrame(data)

# Nome do arquivo com timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"colecoes_{timestamp}.csv"

# Diretório de saída: pasta 'raw' no projeto (relativo ao script)
output_dir = os.path.join(os.getcwd(), "raw")
os.makedirs(output_dir, exist_ok=True)  # cria a pasta se não existir

output_path = os.path.join(output_dir, filename)

# Salvar como CSV
df.to_csv(output_path, index=False)
print(f"✅ Arquivo salvo em: {output_path}")

# Mostrar tempo de execução
execution_time = time.time() - start_time
print(f"⏱️ Tempo de execução: {execution_time:.2f} segundos")
