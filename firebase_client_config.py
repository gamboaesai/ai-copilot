# firebase_client_config.py

from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate("firebase_config.json")
initialize_app(cred)
db = firestore.client()

import pyrebase

firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "your-app.firebaseapp.com",
    "projectId": "your-app",
    "storageBucket": "your-app.appspot.com",
    "messagingSenderId": "SENDER_ID",
    "appId": "APP_ID",
    "databaseURL": "",
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()



