"""
MorningBriefingEngine — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026
Auto-generates daily morning market brief using live Nifty data + Gemini.
"""
import os
import yfinance as yf
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any

load_dotenv()

GEMINI_MODEL = "gemini-2.0-flash"

NIFTY_INDICES = {
    "Nifty 50":     "^NSEI",
    "Nifty Bank":   "^NSEBANK",
    "Nifty IT":     "^CNXIT",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty Auto":   "^CNXAUTO",
    "Nifty FMCG":   "^CNXFMCG",
}


def _configure_gemini():
    try:
        import streamlit as st
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    except Exception:
        api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)


def get_market_snapshot() -> Dict[str, Any]:
    snapshot = {}
    for name, symbol in NIFTY_INDICES.items():
        try:
            fi = yf.Ticker(symbol).fast_info
            last = float(fi.last_price)
            prev = float(fi.previous_close)
            change = round(((last - prev) / prev) * 100, 2) if prev else 0
            snapshot[name] = {"price": round(last, 2), "change_pct": change}
        except Exception:
            snapshot[name] = {"price": 0, "change_pct": 0}
    return snapshot


def generate_morning_briefing() -> str:
    _configure_gemini()
    today    = datetime.now().strftime("%A, %d %B %Y")
    snapshot = get_market_snapshot()

    market_lines = "\n".join([
        f"- {name}: ₹{v['price']:,.2f} ({'+' if v['change_pct']>=0 else ''}{v['change_pct']}%)"
        for name, v in snapshot.items()
    ])
    nifty_chg = snapshot.get("Nifty 50", {}).get("change_pct", 0)
    mood = "BULLISH 🐂" if nifty_chg > 0.5 else "BEARISH 🐻" if nifty_chg < -0.5 else "SIDEWAYS 🦄"

    prompt = f"""You are StockSense AI. Generate today's morning market brief for Indian retail investors.

Date: {today} | Mood: {mood}
Live Data:
{market_lines}

Write in EXACTLY this format:
🌅 **GOOD MORNING — Market Brief | {today}**

📊 **Market Mood**: {mood} — [1-line reason]

🔢 **Index Snapshot**:
[List all 6 indices with ↑ or ↓ arrows]

🎯 **3 Things to Watch Today**:
1. [Sector with interesting movement]
2. [Key Nifty 50 level]
3. [One macro theme]

⚡ **StockSense Signal**: [BUY THE DIP / HOLD / BOOK PROFITS / WAIT — one with reason]

⚠️ Not SEBI-registered advice.
— StockSense AI | NeuralForge

Max 180 words. Sound like a smart friend, not a formal report."""

    try:
        return genai.GenerativeModel(GEMINI_MODEL).generate_content(prompt).text
    except Exception as e:
        return (
            f"🌅 **GOOD MORNING — Market Brief | {today}**\n\n"
            f"📊 **Market Mood**: {mood}\n\n"
            f"🔢 **Index Snapshot**:\n{market_lines}\n\n"
            f"⚠️ AI brief unavailable ({str(e)}). Data is live from NSE.\n"
            f"— StockSense AI | NeuralForge"
        )


if __name__ == "__main__":
    print(generate_morning_briefing())
