import pyrebase


#Pyrebase
config = {
    "apiKey": "AIzaSyB8Uwp_NiacaA_Nl4kZ1o8fGwWVwIo7Q6Y",
    "authDomain": "my-stock-portfolio-db.firebaseapp.com",
    "databaseURL": "https://my-stock-portfolio-db.firebaseio.com",
    "projectId": "my-stock-portfolio-db",
    "storageBucket": "my-stock-portfolio-db.appspot.com",
    "messagingSenderId": "130214519241",
    "appId": "1:130214519241:web:e0426223ced55766b24818",
    "measurementId": "G-SWM8VJ4DZL"
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
db = firebase.database()