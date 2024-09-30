from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd
from datetime import datetime

# Define as variáveis
assunto = "Os melhores Carros para 2024"
url = "https://www.google.com.br/" 
horaAtual = datetime.now().strftime("%H:%M:%S")

# Configura o ChromeDriver usando o ChromeDriverManager
service = Service(ChromeDriverManager().install())

# Inicializa o navegador
nav = webdriver.Chrome(service=service)

# Abre a URL
nav.get(url)

# Aguarde um tempo para a página carregar completamente
time.sleep(2)  

# Localiza o campo de busca, insere o assunto e envia a pesquisa
campo_busca = nav.find_element(By.XPATH, '//*[@name="q"]')
campo_busca.send_keys(assunto)
campo_busca.send_keys(Keys.ENTER)

# Aguarda os resultados carregarem
time.sleep(2)  # Pode ajustar conforme necessário

# Captura os títulos dos resultados da pesquisa
resultados = nav.find_elements(By.XPATH, '//h3')

# Filtra e exibe os títulos válidos
titulos_validos = []
for resultado in resultados:
    texto = resultado.text.strip()
    # Verifica se o título não está vazio e não é patrocinado
    if texto and texto.lower() != 'patrocinado':  
        titulos_validos.append(texto)
        #  Cria um Dataframe
        df = pd.DataFrame({
            'Titulo': titulos_validos,
            'Hora da Pesquisa': [horaAtual] * len(titulos_validos)
            })      
        # Salva o DataFrame em um arquivo Excel
        nomeArquivo = f"C:\Projetos\Automação teste\Entrada\Dados Site.xlsx"

        df.to_excel(nomeArquivo, index=False, engine='openpyxl')

# Fecha o navegador
nav.quit()