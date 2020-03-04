
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
  print(request.json)
  url = request.json
  #chamar a tela para o conteudo
  option = Options()
  option.headless = True
  driver = webdriver.PhantomJS(executable_path='phantomjs.exe')
  
  driver.get(url['url'])
  driver.implicitly_wait(10)  # in seconds

  element =driver.find_element_by_xpath("//div[@class='ui-content']//div[@id='conteudo']")
  html_content = element.get_attribute('outerHTML')

  #2. Parsear o contéudo HTML beaultifulSoup
  soup = BeautifulSoup(html_content, 'html.parser')
  table = soup.find(name='table')
  driver.quit()
  #nome da empresa
  div_Nome_Empresa = soup.find(id='u20')
  #endereço da empresa
  div_CNPJ_ENDERECO = soup.find_all('div', class_ ='text')
  #nome da empresa
  Nome_fantazia = div_Nome_Empresa.text
  #cnpj empresa
  CNPJ = div_CNPJ_ENDERECO[0].text
  #endereço da empresa
  Endereco = div_CNPJ_ENDERECO[1].text
  #removendo espaços em branco 
  CNPJ = ' '.join(CNPJ.split())
  Endereco = ' '.join(Endereco.split())
  CNPJ = CNPJ.replace('CNPJ: ', '')


  #3.Estruturar contéudo em data Frame - Panda
  df_full = pd.read_html(str(table))[0].head()

  df_full.columns = ['Nome', 'Valor']
  topRaking ={}
  topRaking= df_full.to_dict('records')

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
    produtos.append({'id':int(codigo), 'name':produto,'quantidade':quantidade.replace(' ', ''), 'UN': UN.replace(' ', ''), 'valor': VlUnited.replace(' ', ''), 'total': valortotal.replace(' ', '')})
  
  return json.dumps({'Nome':Nome_fantazia,'CNPJ':CNPJ,'Endereço': Endereco,'produtos':produtos})

app.run(debug=True, port=8163)
