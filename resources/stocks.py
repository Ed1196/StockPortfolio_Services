from flask_restful import Resource, reqparse
from models.stocks import StockModel
from flask import request
import security.myJWT
from models.user import UserModel
from flask import request


class StockRetriever(Resource):

    @security.myJWT.requires_auth
    def get(self):
        symbol = request.args.get("symbol")
        # We store the data that we parsed into a Variable
        stock = StockModel(symbol)
        response = stock.getStockInfo()
        if not response:
            return {'success': False,
                    'message': "Alpha Vantage Api calls frequency of 5 per minute or 500 per day has been hit. Please wait."}
        return stock.json()


class StockSearch(Resource):

    @security.myJWT.requires_auth
    def get(self):
        query = request.args.get('query').lower()
        stockList = StockModel.searchStock(query)
        if not stockList:
            return {'success': False,
                    'message': "Alpha Vantage Api calls frequency of 5 per minute or 500 per day has been hit. Please wait."}
        return {'success': True, 'stockList': stockList}




