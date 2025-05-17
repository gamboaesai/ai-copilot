import streamlit as st
import pandas as pd
from datetime import datetime
import openai
import os

# === CONFIG ===
st.set_page_config(page_title="AI Trading Copilot", layout="wide")

# Load API key (you can also use secrets or env vars)
openai.api_key = st.secrets["openai_api_key"] if "openai_api_key" in st.secrets else os.getenv("OPENAI_API_KEY")

# CSV file path
JOURNAL_FILE = "trade_journal.csv"

# === SIDEBAR: TRADE INPUTS ===
st.sidebar.header("🧾 Trade Entry")
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

# === FUNCTION: SAVE TRADE TO CSV ===
def save_trade(data, filename):
    df = pd.DataFrame([data])
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, index=False)

# === FUNCTION: ANALYZE TRADE WITH GPT ===
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

# === PROCESS SUBMISSION ===
if submit_trade:
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

    # Save to CSV
    save_trade(trade_data, JOURNAL_FILE)

    # Analyze trade
    with st.spinner("Analyzing your trade with GPT..."):
        gpt_feedback = analyze_trade(notes)

    st.success("Trade Submitted!")
    st.markdown("### 🧠 GPT Feedback")
    st.info(gpt_feedback)

# === VIEW JOURNAL HISTORY ===
st.markdown("## 📔 Trade Journal History")
if os.path.exists(JOURNAL_FILE):
    journal_df = pd.read_csv(JOURNAL_FILE)
    st.dataframe(journal_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
else:
    st.warning("No trades logged yet.")
