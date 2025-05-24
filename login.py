import streamlit as st
from pyrebase_config import auth

def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error("❌ Login failed. " + str(e))
        return None

def render_login():
    st.title("🔐 Log In to AI Trading Copilot")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        user = login_user(email, password)
        if user:
            st.session_state.user = user
            st.success("✅ Login successful!")
            st.rerun()
