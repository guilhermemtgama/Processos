import requests
import pprint

link = "https://servicodados.ibge.gov.br/api/v3/agregados/7392/periodos/2014/variaveis/10484?localidades=N1[all]"

requisicao = requests.get(link)
informacao = requisicao.json()

#pprint.pprint(informacao[0]["resultados"][0]["series"][0])

item_busca = informacao[0]["variavel"] # variável

resultado = informacao[0]["resultados"][0]["series"][0] # series

print(item_busca)
print(resultado)