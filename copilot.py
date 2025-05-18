# app.py

import streamlit as st
import pandas as pd
from datetime import datetime
import openai
import os
from firebase_client_config import db, auth  # <- Your clean import
from signup import render_signup

# === STREAMLIT CONFIG ===
st.set_page_config(page_title="AI Trading Copilot", layout="wide")

# Load OpenAI API Key
openai.api_key = st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else os.getenv("OPENAI_API_KEY")

# === AUTHENTICATION ===
def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error("Login failed. " + str(e))
        return None

# === FIREBASE JOURNAL SAVE ===
def save_journal(user_id, entry):
    doc_ref = db.collection("journals").document(user_id)
    doc_ref.set({"entries": firestore.ArrayUnion([entry])}, merge=True)

# === GPT ANALYSIS ===
def analyze_trade(entry_text):
    prompt = f"""
You are an AI trading mentor. A trader submitted this journal entry after a trade:

"{entry_text}"

Based on the emotions, confidence, and notes, give:
1. A short summary of what happened.
2. What the trader did well.
3. What could be improved.
4. One specific tip to do better next time.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"⚠️ GPT Analysis failed: {str(e)}"

# === MAIN PAGE ROUTING ===
page = st.sidebar.selectbox("Go to", ["Login", "Sign Up", "Journal"])

# === PAGE: SIGN UP ===
if page == "Sign Up":
    render_signup()

# === PAGE: LOGIN ===
elif page == "Login":
    st.title("🔐 Login to AI Trading Copilot")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.success("Login successful!")
            st.session_state["user"] = user

# === PAGE: JOURNAL ===
elif page == "Journal":
    if "user" not in st.session_state:
        st.warning("Please log in first.")
        st.stop()

    st.title("📔 Trade Journal")

    # === SIDEBAR: TRADE ENTRY ===
    st.sidebar.header("🧾 New Trade Entry")
    trade_pair = st.sidebar.selectbox("Trading Pair", ["MNQ", "NQ", "BTC/USD", "ETH/USD", "SPY", "Custom..."])
    custom_pair = st.sidebar.text_input("Custom Symbol", "") if trade_pair == "Custom..." else ""

    trade_direction = st.sidebar.radio("Direction", ["Long", "Short"])
    position_size = st.sidebar.number_input("Position Size (Contracts)", min_value=1, value=1)
    entry_price = st.sidebar.number_input("Entry Price", min_value=0.0, format="%.2f")
    exit_price = st.sidebar.number_input("Exit Price", min_value=0.0, format="%.2f")
    setup_type = st.sidebar.text_input("Setup Type", placeholder="e.g., Reversal, Breakout")
    confidence = st.sidebar.slider("Confidence Level", 1, 5, 3)
    emotions = st.sidebar.text_input("Emotions/State", placeholder="e.g., Anxious, Calm, Focused")
    notes = st.sidebar.text_area("Trade Notes / Journal Entry")

    submit_trade = st.sidebar.button("✅ Submit Trade")

    # === ON SUBMIT ===
    if submit_trade:
        user_id = st.session_state["user"]["localId"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symbol = custom_pair if trade_pair == "Custom..." else trade_pair
        pnl = (exit_price - entry_price) * position_size if trade_direction == "Long" else (entry_price - exit_price) * position_size

        trade_data = {
            "Timestamp": timestamp,
            "Symbol": symbol,
            "Direction": trade_direction,
            "Size": position_size,
            "Entry Price": entry_price,
            "Exit Price": exit_price,
            "PnL": round(pnl, 2),
            "Setup": setup_type,
            "Confidence": confidence,
            "Emotions": emotions,
            "Notes": notes
        }

        # Save to Firestore
        save_journal(user_id, trade_data)

        with st.spinner("Analyzing your trade..."):
            gpt_feedback = analyze_trade(notes)

        st.success("Trade saved and analyzed!")
        st.markdown("### 🧠 GPT Feedback")
        st.info(gpt_feedback)
