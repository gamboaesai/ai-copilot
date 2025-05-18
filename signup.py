# signup.py

import streamlit as st
from firebase_client_config import auth

def signup_user(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error("Signup failed. " + str(e))
        return None

def render_signup():
    st.title("📝 Sign Up for AI Trading Copilot")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if password != confirm_password:
            st.warning("Passwords do not match.")
        else:
            user = signup_user(email, password)
            if user:
                st.success("Signup successful! Please log in.")
