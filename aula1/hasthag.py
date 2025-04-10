import pyautogui
import time
import pandas as pd

# Para ele executar cada ação com atraso de 0.5
pyautogui.PAUSE = 1

   # Abrir google
pyautogui.press("win")
pyautogui.write("google")
pyautogui.press("enter")

time.sleep(1.5)
# Ir a web desejada
pyautogui.write("https://dlp.hashtagtreinamentos.com/python/intensivao/login")
pyautogui.press("enter")

# Aguarde um tempo para conectar tudo
time.sleep(2.5)

# Ir ao email do formulario
pyautogui.moveTo(x=790, y=371)
pyautogui.click()    

# Logar
pyautogui.write("teste@gmail.com")
pyautogui.press("tab")
pyautogui.write("1234")
pyautogui.press("tab")
pyautogui.press("enter")

# Abrir base de produtos
tabela = pd.read_csv("produtos.csv")

# Para cada linha da tabela
for index, linha in tabela.iterrows():
    pyautogui.moveTo(x=928, y=252)
    pyautogui.click()
    pyautogui.write(str(linha["codigo"]))
    pyautogui.press("tab")
    pyautogui.write(str(linha["marca"]))
    pyautogui.press("tab")
    pyautogui.write(str(linha["tipo"]))
    pyautogui.press("tab")
    pyautogui.write(str(linha["categoria"]))
    pyautogui.press("tab")
    pyautogui.write(str(linha["preco_unitario"]))
    pyautogui.press("tab")
    pyautogui.write(str(linha["custo"]))
    pyautogui.press("tab")
    obs = str(linha["obs"])
    if obs != "nan":
       pyautogui.write(obs)
    pyautogui.press("tab")
    pyautogui.press("enter")

