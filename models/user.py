from dbAccess import auth, db
from collections import OrderedDict
from decimal import Decimal
from flask import jsonify
from datetime import date
from models.stocks import StockModel


class UserModel():
    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.user = ''
        self.account = '5000.00'
        self.mystocks = []

    def json(self):
        return {
            'firtsname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'account': self.account,
        }

    def save_to_db(self):
        # Add account to user authentication list
        self.user = auth.create_user_with_email_and_password(self.email, self.password)
        # Add account details to database
        dbUser = {"firstname": self.firstname, "lastname": self.lastname, "email": self.email, "account": self.account}

        # This creates the path: Users - userID - user information. This is saved separtly from where the auth info
        # is saved. This saves the user to the actual database in firebase
        db.child("users").child(self.user["localId"]).set(dbUser)

    def send_ver_email(self):
        auth.send_email_verification(self.user["idToken"])

    def auth(self):
        self.user = auth.sign_in_with_email_and_password(self.email, self.password)
        return self.user

    @classmethod
    def purchase_stock(cls, quantity, price: float, symbol, localId, open):
        # Retrieve user account
        user = db.child("users").child(localId).child("account")
        # Retrieve the account balance
        currentBalance = float(user.get().val());
        # Calculate new balance
        newBalance = round(Decimal(round(Decimal(currentBalance), 2) - round(Decimal(quantity * price), 2)), 2)
        if newBalance < 0:
            return False
        usersInfo = db.child("users").child(localId).child("mystocks").get()
        # STOCK DIRECTORY DOES NOT EXISTS, FIRST TIME BUYER
        if usersInfo.val() is None:
            UserModel.set__balance_stocks(localId, newBalance, symbol, price, quantity, open)
            UserModel.log_transaction(symbol, quantity, price, localId)
            UserModel.create_portfolio(localId, quantity, price)

            return True
        # STOCK HAS BEEN PURCHASED BEFORE
        else:
            # Loops over the users purchased stocks
            for stock in usersInfo.each():
                # stores stock Tricker Symbol and dic {price, quantity} in a tuple
                userStocks = (stock.key(), stock.val())
                # check if the stock user is trying to buy is already on the porfolio
                if symbol in userStocks[0]:
                    # Add the quantity in of the stock in the portfolio and the quantity of the stocks user is trying to
                    # purchase
                    newQuantity: int = userStocks[1]['quantity'] + quantity
                    UserModel.update_balance_stocks(localId, symbol, price, newQuantity, newBalance, open)
                    UserModel.log_transaction(symbol, quantity, price, localId)
                    UserModel.update_portfolio(localId, quantity, price)
                    return True
            # STOCK NOT IN LIST, BUT HAS BOUGHT STOCKS BEFORE
            else:
                UserModel.set__balance_stocks(localId, newBalance, symbol, price, quantity, open)
                UserModel.log_transaction(symbol, quantity, price, localId)
                UserModel.update_portfolio(localId, quantity, price)
                return True

        return False

    @classmethod
    def get_user_details(cls, localId):
        user = db.child("users").child(localId).get()
        userDetails = {}
        for details in user.each():
            userDetails[details.key()] = details.val()
        return userDetails

    @classmethod
    def find_by_id_token(cls, userId):
        return auth.get_account_info(userId)

    @classmethod
    def set__balance_stocks(cls, localId, newBalance, symbol, price, quantity, open):
        db.child("users").child(localId).update({"account": str(newBalance)})
        transaction = {"symbol": symbol, "quantity": quantity, "price": price, "open": open}
        db.child("users").child(localId).child("mystocks").child(symbol).set(transaction)

    @classmethod
    def update_balance_stocks(cls, localId, symbol, price, newQuantity, newBalance, open):
        # Update to firebase
        transaction = {"symbol": symbol, "quantity": newQuantity, "price": price, "open": open}
        db.child("users").child(localId).child("mystocks").child(symbol).update(transaction)
        db.child("users").child(localId).update({"account": str(newBalance)})

    @classmethod
    def log_transaction(cls, symbol, quantity, price, localId):
        transaction = {"symbol": symbol, "quantity": quantity, "price": price}
        db.child("users").child(localId).child("transactions").push(transaction)

    @classmethod
    def create_portfolio(cls, localId, quantity, price):
        portfolio = round(Decimal(quantity * price) , 2)
        portfolioValFormat = str(portfolio)
        db.child("users").child(localId).child("totalportfolio").set(portfolioValFormat)

    @classmethod
    def update_portfolio(cls, localId, quantity, price):
        currentPortfolio = db.child("users").child(localId).child("totalportfolio").get().val()
        # stores stock Tricker Symbol and dic {price, quantity} in a tuple
        updatePortfolio = round( ( Decimal(float(currentPortfolio)) + Decimal(quantity * price)),2 )
        portfolioValFormat = str(updatePortfolio)
        db.child("users").child(localId).child("totalportfolio").set(portfolioValFormat)

    @classmethod
    def check_stock_changes(cls, localId):
        userStocks = db.child("users").child(localId).child("mystocks").get()
        currentPortfolio: float = 0
        stocksDict = {}
        for stock in userStocks.each():
            # Get stock value from db
            userStocks = (stock.key(), stock.val())
            try:
                # Get stock value from Alpha Vantage API
                currentStock = StockModel.getStockLatestInfo(userStocks[0])
            except:
                return False

            if not currentStock:
                return False

            if userStocks[1]['price'] != currentStock['close']:
                db.child("users").child(localId).child("mystocks").child(userStocks[0]).update(
                    {'price': currentStock['close']})
                stocksDict[userStocks[0]] = {"price": currentStock['close'],
                                             "quantity": userStocks[1]['quantity'], "open": currentStock['open']}

                currentPortfolio = currentPortfolio + round(Decimal(userStocks[1]['quantity'] * currentStock['close']), 2)
            else:
                stocksDict[userStocks[0]] = {"price": userStocks[1]['price'],
                                             "quantity": userStocks[1]['quantity'], "open": currentStock['open']}
                currentPortfolio = currentPortfolio + round(Decimal(userStocks[1]['quantity'] * userStocks[1]['price']), 2)

            db.child("users").child(localId).child("mystocks").child(userStocks[0]).child("open").set(currentStock['open'])

        db.child("users").child(localId).child("totalportfolio").set(str(currentPortfolio))

        return (stocksDict, str(currentPortfolio))

    @classmethod
    def check_stock_changes_compact(cls, localId, stockList):
        userStocks = db.child("users").child(localId).child("mystocks").get()
        currentPortfolio: float = 0
        stocksDict = {}
        for stock in userStocks.each():
            # Get stock value from db
            userStocks = (stock.key(), stock.val())

            if userStocks[0] in stockList:
                try:
                    # Get stock value from Alpha Vantage API
                    currentStock = StockModel.getStockLatestInfo(userStocks[0])
                    currentStock['price'] = currentStock['close']

                except:
                    return False
            else:
                currentStock = stock.val()
                currentStock['close'] = currentStock['price']

            if not currentStock:

                return False

            if userStocks[1]['price'] != currentStock['close']:
                db.child("users").child(localId).child("mystocks").child(userStocks[0]).update(
                    {'price': currentStock['price']})
                stocksDict[userStocks[0]] = {"price": currentStock['close'],
                                             "quantity": userStocks[1]['quantity'], "open": currentStock['open']}

                currentPortfolio = currentPortfolio + round(Decimal(userStocks[1]['quantity'] * currentStock['close']),
                                                            2)
            else:
                stocksDict[userStocks[0]] = {"price": userStocks[1]['price'],
                                             "quantity": userStocks[1]['quantity'], "open": currentStock['open']}
                currentPortfolio = currentPortfolio + round(Decimal(userStocks[1]['quantity'] * userStocks[1]['price']),
                                                            2)

            db.child("users").child(localId).child("mystocks").child(userStocks[0]).child("open").set(
                currentStock['open'])

        db.child("users").child(localId).child("totalportfolio").set(str(currentPortfolio))

        return (stocksDict, str(currentPortfolio))

    @classmethod
    def refresh_token(cls, refreshToken):
        user = auth.refresh(refreshToken)
        return user
