import requests
import re
import investpy
from bs4 import BeautifulSoup

response = requests.get("http://localhost:8000/stored")
print(response.json())

# response = requests.get("https://api.dadosdemercado.com.br/v1/auth")
x = investpy.stocks.get_stocks(country = "brazil")[["name", "symbol"]]
x.columns = ["company_name", "ticker"]
x = x.to_dict("records")
print(x)

response = requests.post("http://localhost:8000/store_tickers", json = {"empresas": x})
print(response.text)

# empresas = soup.find_all("td")
# tickers = soup.find_all("a") 

# print(len(empresas), len(tickers))

# empresas = [empresa.text for empresa in empresas]
# print(empresas)
# tickers = [ticker.text for ticker in tickers]
# print(tickers)

# empresas = [empresa.text.split(' ')[0].lower() for empresa in empresas]
# print(len(empresas))

# tickers = soup.find_all("td", class_ = "strong")
# tickers = [ticker.text.replace("\n", "") for ticker in tickers]
# print(len(tickers))

# tickers_dict = {empresa:ticker for empresa, ticker in zip(empresas, tickers)}
# print(tickers_dict)

# response = requests.post("http://localhost:8000/get_ticker", json = {"company_name":"natura"})
# print(response.json())