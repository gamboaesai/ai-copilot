import streamlit as st
import os
from datetime import datetime
import openai
from firebase_admin import firestore
from firebase_client_config import db  # Ensure this initializes Firebase
import streamlit as st
def main():
    # all your existing copilot UI code


# Check if user is logged in
if "user" not in st.session_state:
    st.warning("🔐 Please log in to access the Trading Copilot.")
    st.stop()

user_id = st.session_state.user["localId"]

# === CONFIG ===
st.set_page_config(page_title="AI Trading Copilot", layout="wide")

# Load OpenAI API key
openai.api_key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")

# === FUNCTIONS ===
def save_trade_to_firebase(user_id, trade_data):
    try:
        doc_ref = db.collection("journals").document(user_id)
        doc_ref.set({"entries": firestore.ArrayUnion([trade_data])}, merge=True)
        return True
    except Exception as e:
        st.error(f"❌ Failed to save trade: {e}")
        return False

def load_trades_from_firebase(user_id):
    try:
        doc_ref = db.collection("journals").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("entries", [])
        return []
    except Exception as e:
        st.error(f"❌ Failed to load trades: {e}")
        return []

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

# === UI ===
st.title("🧠 AI Trading Copilot")

user_id = st.text_input("Enter your User ID to access your journal entries:")

st.sidebar.header("🧾 Trade Entry")
trade_pair = st.sidebar.selectbox("Trading Pair", ["MNQ", "NQ", "BTC/USD", "ETH/USD", "SPY", "Custom..."])
custom_pair = st.sidebar.text_input("Custom Symbol") if trade_pair == "Custom..." else ""

trade_direction = st.sidebar.radio("Direction", ["Long", "Short"])
position_size = st.sidebar.number_input("Position Size (Contracts)", min_value=1, value=1)
entry_price = st.sidebar.number_input("Entry Price", min_value=0.0, format="%.2f")
exit_price = st.sidebar.number_input("Exit Price", min_value=0.0, format="%.2f")
setup_type = st.sidebar.text_input("Setup Type (e.g., Reversal, Breakout)")
confidence = st.sidebar.slider("Confidence Level", 1, 5, 3)
emotions = st.sidebar.text_input("Emotions/State (e.g., Calm, Anxious, Focused)")
notes = st.sidebar.text_area("Trade Notes / Journal Entry")

submit_trade = st.sidebar.button("✅ Submit Trade")

if submit_trade:
    if not user_id:
        st.error("Please enter your User ID before submitting a trade.")
    else:
        symbol = custom_pair if trade_pair == "Custom..." else trade_pair
        pnl = (exit_price - entry_price) * position_size if trade_direction == "Long" else (entry_price - exit_price) * position_size
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with st.spinner("Analyzing your trade with GPT..."):
            gpt_feedback = analyze_trade_with_gpt(notes)

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
            "Notes": notes,
            "GPT_Feedback": gpt_feedback
        }

        saved = save_trade_to_firebase(user_id, trade_data)

        if saved:
            st.success("✅ Trade Submitted and Saved!")
            if pnl >= 0:
                st.success(f"PnL: +${pnl:.2f}")
            else:
                st.error(f"PnL: -${abs(pnl):.2f}")

            st.markdown("### 💬 GPT Feedback")
            st.info(gpt_feedback)

# === Display previous trades ===
if user_id:
    st.markdown("## 📊 Your Past Trades")
    past_trades = load_trades_from_firebase(user_id)

    if past_trades:
        for i, trade in enumerate(reversed(past_trades[-5:]), 1):  # Show last 5 trades
            with st.expander(f"{trade['Timestamp']} — {trade['Symbol']} ({trade['Direction']})"):
                st.write(trade)
    else:
        st.info("No trades found for this user.")
