import firebase_admin
from firebase_admin import credentials, firestore

# Path to your Firebase service account key JSON
SERVICE_ACCOUNT_PATH = "firebase_config.json"

# Initialize Firebase app only once
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

# Create Firestore client
db = firestore.client()
