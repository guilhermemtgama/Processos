import requests
import json
import time
from datetime import datetime

cotacoes = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL")
cotacoes = cotacoes.json()

# print(cotacoes)
Contador = 1
while Contador <= 10:
    hora_Consulta = datetime.now().strftime("%H:%M:%S")
    print(f"Cotação: {Contador}°"" Nova cotação")
    # Cotações Bitcoin
    nome_Cotacao = cotacoes["BTCBRL"]["name"]
    cotacao_Btc = cotacoes["BTCBRL"]["bid"]
    print(nome_Cotacao, ": ", cotacao_Btc)
    # Cotações Euro
    nome_Cotacao = cotacoes["EURBRL"]["name"]
    cotacao_Euro = cotacoes["EURBRL"]["bid"]
    print(nome_Cotacao, ": ", cotacao_Euro)
    # Cotações Dolar
    nome_Cotacao = cotacoes["USDBRL"]["name"]
    cotacao_Dolar = cotacoes["USDBRL"]["bid"]
    print(nome_Cotacao, ": ", cotacao_Dolar)
    print("Hora da consulta: {0}".format(hora_Consulta)) 
    time.sleep(30)
    Contador += 1
