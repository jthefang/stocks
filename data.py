import requests


API_KEY = "NL04VP2IPHMIWGSI"


def get_stock_data(ticker: str):
  url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={API_KEY}"
  r = requests.get(url)
  data = r.json()
  return data

