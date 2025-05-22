import streamlit as st
from pyrebase_config import auth

def signup_user(email, password):
    try:
        return auth.create_user_with_email_and_password(email, password)
    except Exception as e:
        st.error(f"Signup failed: {e}")
        return None

def render_signup():
    st.title("📝 Sign Up")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):
        if password != confirm:
            st.warning("Passwords do not match.")
        else:
            user = signup_user(email, password)
            if user:
                st.success("Signup successful. You can now log in.")

