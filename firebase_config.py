import firebase_admin
from firebase_admin import credentials, firestore
import json
import streamlit as st

if not firebase_admin._apps:
    # Load from Streamlit secrets.toml
    cred_dict = json.loads(st.secrets["firebase_config"])
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
