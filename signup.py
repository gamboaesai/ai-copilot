import streamlit as st
from firebase_client_config import auth
from signup import render_signup

def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error("Login failed. " + str(e))
        return None

def render_login():
    st.title("🔐 Login to AI Trading Copilot")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.success("Login successful!")
            st.session_state['user'] = user
