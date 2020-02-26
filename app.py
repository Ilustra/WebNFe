
from flask import Flask
from flask import request

import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json


app = Flask("wtf")

@app.route("/nfe", methods=["GET", "POST"])
def nfe():
  
  url = request.json
  #chamar a tela para o conteudo
  option = Options()
  option.headless = True
  driver = webdriver.Firefox(executable_path='C:\\Python27\\geckodriver.exe')
  print(url.values)
  driver.get(url['url'])
  driver.implicitly_wait(10)  # in seconds

  element =driver.find_element_by_xpath("//div[@class='ui-content']//div[@id='conteudo']//table")
  html_content = element.get_attribute('outerHTML')
  #2. Parsear o contéudo HTML beaultifulSoup
  soup = BeautifulSoup(html_content, 'html.parser')
  table = soup.find(name='table')
  #3.Estruturar contéudo em data Frame - Panda
  df_full = pd.read_html(str(table))[0].head()
  df_full.columns = ['Nome', 'Valor']
  topRaking ={}
  topRaking= df_full.to_dict('records')

  print(topRaking)
  #separar produtos e transformar e json
  produtos=[]
  for value in topRaking:
    #separar o codigo do produto da string nome
    produto = value['Nome'][0:value['Nome'].find('(')]
    codigo = value['Nome'][value['Nome'].find('(')+1:value['Nome'].find(')')].replace('Código: ', '')
    quantidade = value['Nome'][value['Nome'].index('Qtde'):value['Nome'].index('UN')].replace('Qtde.:', '')
    UN = value['Nome'][value['Nome'].index('UN:'):value['Nome'].index('Vl')].replace('UN:', '')
    VlUnited = value['Nome'][value['Nome'].index('Unit'):].replace('Unit.: ', '')
    valortotal =value['Valor'].replace('Vl. Total', '')
    produtos.append({'Codigo':codigo, 'Nome':produto,'Quantidade':quantidade.replace(' ', ''), 'UN': UN.replace(' ', ''), 'Valor': VlUnited.replace(' ', ''), 'Total': valortotal.replace(' ', '')})

  return json.dumps(produtos)

app.run(debug=True)
