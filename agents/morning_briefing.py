"""
MorningBriefingEngine — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026

Auto-generates a daily morning market brief using live Nifty data + Gemini.
Produces WhatsApp-style market update, zero human editing required.
"""

import os
import yfinance as yf
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any

load_dotenv()

NIFTY_INDICES = {
    "Nifty 50": "^NSEI",
    "Nifty Bank": "^NSEBANK",
    "Nifty IT": "^CNXIT",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty Auto": "^CNXAUTO",
    "Nifty FMCG": "^CNXFMCG"
}


def _configure_gemini():
    """Configure Gemini with API key."""
    try:
        import streamlit as st
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    except Exception:
        api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)


def get_market_snapshot() -> Dict[str, Any]:
    """Fetch live Nifty indices snapshot via yfinance."""
    snapshot = {}
    for name, symbol in NIFTY_INDICES.items():
        try:
            ticker = yf.Ticker(symbol)
            fast = ticker.fast_info
            last = float(fast.last_price)
            prev = float(fast.previous_close)
            change_pct = round(((last - prev) / prev) * 100, 2) if prev else 0
            snapshot[name] = {"price": round(last, 2), "change_pct": change_pct}
        except Exception:
            snapshot[name] = {"price": 0, "change_pct": 0}
    return snapshot


def generate_morning_briefing() -> str:
    """
    Auto-generate today's morning market brief.
    Combines live Nifty data + Gemini LLM into a WhatsApp-style brief.
    """
    _configure_gemini()
    today = datetime.now().strftime("%A, %d %B %Y")
    snapshot = get_market_snapshot()

    market_lines = "\n".join([
        f"- {name}: ₹{v['price']:,.2f} ({'+' if v['change_pct'] >= 0 else ''}{v['change_pct']}%)"
        for name, v in snapshot.items()
    ])

    # Determine overall mood
    nifty_change = snapshot.get("Nifty 50", {}).get("change_pct", 0)
    mood = "BULLISH 🐂" if nifty_change > 0.5 else "BEARISH 🐻" if nifty_change < -0.5 else "SIDEWAYS 🦄"

    prompt = f"""You are StockSense AI — generate today's morning market brief for Indian retail investors.

Date: {today}
Overall Mood: {mood}

Live Nifty Data:
{market_lines}

Write a WhatsApp-style morning brief in EXACTLY this format:

🌅 **GOOD MORNING — Market Brief | {today}**

📊 **Market Mood**: {mood} — [1-line reason based on data]

🔢 **Index Snapshot**:
[List ALL 6 indices from data with arrows: ↑ or ↓]

🎯 **3 Things to Watch Today**:
1. [Sector with interesting movement]
2. [Key Nifty 50 level to monitor]
3. [One macro theme active today]

⚡ **StockSense Signal**: [BUY THE DIP / HOLD / BOOK PROFITS / WAIT — choose ONE with reason]

⚠️ Not SEBI-registered investment advice. For educational purposes only.
— StockSense AI | NeuralForge

Max 180 words. Sound like a smart, helpful friend — not a formal report."""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(prompt).text
    except Exception as e:
        # Fallback briefing
        return f"""🌅 **GOOD MORNING — Market Brief | {today}**

📊 **Market Mood**: {mood}

🔢 **Index Snapshot**:
{market_lines}

⚠️ AI brief unavailable ({str(e)}). Data is live from NSE.
— StockSense AI | NeuralForge"""


if __name__ == "__main__":
    print("Testing MorningBriefingEngine...")
    brief = generate_morning_briefing()
    print(brief)
