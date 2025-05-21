# pyrebase_config.py

import pyrebase
import json

# Replace these with your Firebase project's web app config
firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_PROJECT.firebaseapp.com",
    "databaseURL": "",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT.appspot.com",
    "messagingSenderId": "SENDER_ID",
    "appId": "APP_ID",
    "measurementId": "MEASUREMENT_ID"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
