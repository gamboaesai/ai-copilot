import streamlit as st
from login import render_login
from firebase_setup import db
from datetime import datetime
import pandas as pd
import openai
import os

# === CONFIG ===
st.set_page_config(page_title="AI Trading Copilot", layout="wide")
openai.api_key = st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else os.getenv("OPENAI_API_KEY")

# === LOGIN CHECK ===
if 'user' not in st.session_state:
    render_login()
    st.stop()

# === TRADE ENTRY ===
st.sidebar.header("🧾 Trade Entry")
trade_pair = st.sidebar.selectbox("Trading Pair", ["MNQ", "NQ", "BTC/USD", "ETH/USD", "SPY", "Custom..."])
custom_pair = st.sidebar.text_input("Custom Symbol", "") if trade_pair == "Custom..." else ""
trade_direction = st.sidebar.radio("Direction", ["Long", "Short"])
position_size = st.sidebar.number_input("Position Size", min_value=1, value=1)
entry_price = st.sidebar.number_input("Entry Price", min_value=0.0, format="%.2f")
exit_price = st.sidebar.number_input("Exit Price", min_value=0.0, format="%.2f")
setup_type = st.sidebar.text_input("Setup Type")
confidence = st.sidebar.slider("Confidence Level", 1, 5, 3)
emotions = st.sidebar.text_input("Emotions")
notes = st.sidebar.text_area("Notes")
submit_trade = st.sidebar.button("✅ Submit Trade")

def analyze_trade(notes):
    prompt = f"""You are an AI trading mentor. A trader submitted this journal entry:
"{notes}"
Provide:
1. Summary
2. What was done well
3. What to improve
4. Tip for next time
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
        return f"GPT Error: {str(e)}"

def save_trade(user_id, entry_data):
    db.collection("journals").document(user_id).set({
        "entries": firestore.ArrayUnion([entry_data])
    }, merge=True)

if submit_trade:
    symbol = custom_pair if trade_pair == "Custom..." else trade_pair
    pnl = (exit_price - entry_price) * position_size if trade_direction == "Long" else (entry_price - exit_price) * position_size
    timestamp = datetime.now().isoformat()

    trade_entry = {
        "timestamp": timestamp,
        "symbol": symbol,
        "direction": trade_direction,
        "size": position_size,
        "entry": entry_price,
        "exit": exit_price,
        "pnl": round(pnl, 2),
        "setup": setup_type,
        "confidence": confidence,
        "emotions": emotions,
        "notes": notes
    }

    save_trade(st.session_state['user']['localId'], trade_entry)

    with st.spinner("Analyzing your trade..."):
        analysis = analyze_trade(notes)

    st.success("Trade submitted!")
    st.markdown("### 🧠 GPT Feedback")
    st.info(analysis)
