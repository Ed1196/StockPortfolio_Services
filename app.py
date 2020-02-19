from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from datetime import timedelta

#Endpoint to register user
from resources.user import UserRegister, UserLogin, UserInfo, UpdateMyStock, UpdateMyStockCompact, TokenRefresh

#Endpoint to get stock info
from resources.stocks import StockRetriever
from resources.stocks import StockSearch
from resources.transactions import Transactions

#Use to enable CORS for all domains
from flask_cors import CORS


app = Flask(__name__)
api = Api(app)

#This fixes the 'XMLHttpsRequest has been blocked by CORS policy'
#It will enable CORS support on all routes, for all origins and methods.
CORS(app)

@app.route("/", methods=['GET'])
def HelloWord():
    return "Hello World"

#Decryption Key
app.secret_key = 'Edwin'


api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(StockRetriever, '/stock')
api.add_resource(StockSearch, '/stock-search')
api.add_resource(Transactions, '/purchase')
api.add_resource(UserInfo, '/userinfo')
api.add_resource(UpdateMyStock, '/update-info')
api.add_resource(UpdateMyStockCompact, '/update-info-compact')
api.add_resource(TokenRefresh, '/refresh-token')


'''
@jwt.auth_response_handler
def customized_response_handler(access_token, identity):
    return jsonify({
        'authorization' : access_token.decode('utf-8'),
        'user_id' : identity.id
    })
'''

if __name__ == '__main__':
    app.run(port=5000, debug=True)
