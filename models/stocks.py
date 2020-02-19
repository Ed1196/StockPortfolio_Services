import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from flask import request
import requests
import time

from donotexport.myKey import MyKey

# Remove when in production
key = MyKey()
api_url = "https://www.alphavantage.co"


class StockModel():
    def __init__(self, symbol):
        self.symbol = symbol
        self.open: float = 0
        self.high: float = 0
        self.low: float = 0
        self.close: float = 0
        self.volume: float = 0
        self.change: float = 0


    def json(self):
        return {

            'symbol': self.symbol,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'date': self.date,
            'change': self.change
        }

    def getStockInfo(self):
        api_key = key.returnKey()
        try:
            ts = TimeSeries(key=api_key, output_format='pandas')
            data, meta_data = ts.get_quote_endpoint(symbol=self.symbol)
        except:
            return False
        self.open = float(data['02. open'][0])
        self.high = float(data['03. high'][0])
        self.low = float(data['04. low'][0])
        self.close = float(data['05. price'][0])
        self.volume = float(data['06. volume'][0])
        self.date = str(data['07. latest trading day'][0])
        self.change = float(data['09. change'])
        return True


    @classmethod
    def searchStock(self, query):
        """
        Search stock via Ticker Symbol

        URL Parameters:
            query: string, required
        :return string:
        """
        api_key = key.returnKey()
        response = requests.get(api_url + "/query?function=SYMBOL_SEARCH&keywords=" + query + "&apikey=" + api_key)
        if 'Note' in response.json():
            return False
        stockList = response.json()
        list = stockList['bestMatches']
        ret = []

        if len(list) == 0:
            return []

        for stock in list:
            ret.append(stock['1. symbol'])
        return ret

    @classmethod
    def getStockLatestInfo(cls, symbol):
        api_key = key.returnKey()
        try:
            ts = TimeSeries(key=api_key, output_format='pandas')
            data, meta_data = ts.get_quote_endpoint(symbol=symbol)
        except:
            return False
        stock = StockModel(data['01. symbol'][0])
        stock.open = float(data['02. open'][0])
        stock.high = float(data['03. high'][0])
        stock.low = float(data['04. low'][0])
        stock.close = float(data['05. price'][0])
        stock.volume = float(data['06. volume'][0])
        stock.date = str(data['07. latest trading day'][0])
        stock.change = float(data['09. change'])
        return stock.json()



