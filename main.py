import streamlit as st
from signup import render_signup
from login import render_login
import copilot  # your main app with `main()` function

# Page config
st.set_page_config(page_title="AI Trading Copilot", layout="wide")

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["Login", "Sign Up", "Copilot"])

# Route logic
if page == "Login":
    render_login()

elif page == "Sign Up":
    render_signup()

elif page == "Copilot":
    if "user" in st.session_state:
        copilot.main()
    else:
        st.warning("🔐 Please log in to access the Trading Copilot.")
