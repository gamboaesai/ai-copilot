# main.py

import streamlit as st
from signup import render_signup
from login import render_login
import copilot

st.set_page_config(page_title="AI Trading Copilot", layout="centered")

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["Login", "Sign Up", "App"])

if page == "Login":
    render_login()
elif page == "Sign Up":
    render_signup()
elif page == "App":
    if "user" in st.session_state:
        copilot.main()
    else:
        st.warning("Please log in first.")
