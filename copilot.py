import streamlit as st
import os
from datetime import datetime
import openai
from firebase_client_config import db  # Make sure this initializes Firebase Admin and Firestore

# Set Streamlit page config
st.set_page_config(page_title="AI Trading Copilot", layout="wide")

# Load OpenAI API key
openai.api_key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")

# Sidebar: Trade entry form
st.sidebar.header("🧾 Trade Entry")
trade_pair = st.sidebar.selectbox("Trading Pair", ["MNQ", "NQ", "BTC/USD", "ETH/USD", "SPY", "Custom..."])
custom_pair = st.sidebar.text_input("Custom Symbol") if trade_pair == "Custom..." else ""

trade_direction = st.sidebar.radio("Direction", ["Long", "Short"])
position_size = st.sidebar.number_input("Position Size (Contracts)", min_value=1, value=1)
entry_price = st.sidebar.number_input("Entry Price", min_value=0.0, format="%.2f")
exit_price = st.sidebar.number_input("Exit Price", min_value=0.0, format="%.2f")
setup_type = st.sidebar.text_input("Setup Type", placeholder="e.g., Reversal, Breakout")
confidence = st.sidebar.slider("Confidence Level", 1, 5, 3)
emotions = st.sidebar.text_input("Emotions/State", placeholder="e.g., Anxious, Calm, Focused")
notes = st.sidebar.text_area("Trade Notes / Journal Entry")

submit_trade = st.sidebar.button("✅ Submit Trade")

# Function to save trade entry in Firebase Firestore
def save_trade_to_firebase(user_id, trade_data):
    if not user_id:
        st.error("User ID is required to save a trade.")
        return False
    try:
        doc_ref = db.collection("journals").document(user_id)
        doc_ref.set({"entries": firestore.ArrayUnion([trade_data])}, merge=True)
        return True
    except Exception as e:
        st.error(f"Failed to save trade: {e}")
        return False

# Function to analyze trade notes using OpenAI GPT
def analyze_trade_with_gpt(notes_text):
    prompt = f"""
You are an AI trading mentor. A trader submitted this journal entry after a trade:

"{notes_text}"

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
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ GPT Analysis failed: {e}"

# Main app UI
st.title("AI Trading Copilot")

user_id = st.text_input("Enter your User ID to save your journal entries:")

if submit_trade:
    if not user_id:
        st.error("Please enter your User ID before submitting a trade.")
    else:
        symbol = custom_pair if trade_pair == "Custom..." else trade_pair
        pnl = (exit_price - entry_price) * position_size if trade_direction == "Long" else (entry_price - exit_price) * position_size
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

        saved = save_trade_to_firebase(user_id, trade_data)

        if saved:
            with st.spinner("Analyzing your trade with GPT..."):
                gpt_feedback = analyze_trade_with_gpt(notes)

            st.success("Trade Submitted and Saved!")
            st.markdown("### 🧠 GPT Feedback")
            st.info(gpt_feedback)
