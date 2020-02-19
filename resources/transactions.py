from flask_restful import Resource, reqparse

import security.myJWT
from models.user import UserModel
from flask import request



class Transactions(Resource):
    # Variable that will allow us to parse the data when given a request
    parser = reqparse.RequestParser()

    # Specify what we want from the payload
    parser.add_argument('quantity',
                        type=float,
                        required=True,
                        help='This field cannot be left blank!')

    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This field cannot be left blank!')

    parser.add_argument('symbol',
                        type=str,
                        required=True,
                        help='This field cannot be left blank!')

    parser.add_argument('open',
                        type=float,
                        required=True,
                        help='This field cannot be left blank!')

    # Post Request
    @security.myJWT.requires_auth
    def post(self):
        # We store the data that we parsed into a Variable

        data = Transactions.parser.parse_args()
        tokenInfo = UserModel.find_by_id_token(request.idToken)
        localId = tokenInfo['users'][0]['localId']

        aproved = UserModel.purchase_stock(data['quantity'], data['price'], data['symbol'], localId, data['open'])
        userDetails = UserModel.get_user_details(localId)

        if aproved:
            return {'success': True, 'userdetails': userDetails}, 201

        return {'success': False, 'message': 'Not enough credits!'}, 201
