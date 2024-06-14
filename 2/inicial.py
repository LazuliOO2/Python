from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import openpyxl

# Inicializa o driver do Selenium (neste exemplo, estou usando o Chrome)
driver = webdriver.Chrome()

# Abre a página da web
driver.get('https://contabilidade-devaprender.netlify.app/')
sleep(5)

# Fazer login
email = driver.find_element(By.XPATH,"//input[@id='email']")
sleep(2)
email.send_keys('olazulioo2@gmail.com')
senha = driver.find_element(By.XPATH,"//input[@id='senha']")
sleep(2)
senha.send_keys('1234')
login = driver.find_element(By.XPATH,"//button[@id='Entrar']")
sleep(2)
login.click()
sleep(5)

empresa = openpyxl.load_workbook('./empresas.xlsx')
pagina_empresa = empresa ['dados empresas']

for linha in pagina_empresa.iter_rows(min_row=2, values_only=True):
    nome_empresa, email, telefone, endereço, cnpj, area_atuação, quantidade_de_funcionarios, data_fundação = linha

    driver.find_element(By.ID, 'nomeEmpresa').send_keys(nome_empresa)
    sleep(1)
    driver.find_element(By.ID, 'emailEmpresa').send_keys(email)
    sleep(1)
    driver.find_element(By.ID, 'telefoneEmpresa').send_keys(telefone)
    sleep(1)
    driver.find_element(By.ID, 'enderecoEmpresa').send_keys(endereço)
    sleep(1)
    driver.find_element(By.ID, 'cnpj').send_keys(cnpj)
    sleep(1)
    driver.find_element(By.ID, 'areaAtuacao').send_keys(area_atuação)
    sleep(1)
    driver.find_element(By.ID, 'numeroFuncionarios').send_keys(quantidade_de_funcionarios)
    sleep(1)
    driver.find_element(By.ID, 'dataFundacao').send_keys(data_fundação)
    sleep(1)

    driver.find_element(By.ID,'Cadastrar').click()
    sleep(3)

    driver.quit()
