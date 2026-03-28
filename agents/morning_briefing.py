"""
MorningBriefingEngine — StockSense AI | NeuralForge
Gemini 2.0 Flash → HuggingFace → rule-based fallback.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yfinance as yf
from datetime import datetime
from typing import Dict, Any
from agents.llm_router import call_llm

NIFTY_INDICES = {
    "Nifty 50":     "^NSEI",
    "Nifty Bank":   "^NSEBANK",
    "Nifty IT":     "^CNXIT",
    "Nifty Pharma": "^CNXPHARMA",
    "Nifty Auto":   "^CNXAUTO",
    "Nifty FMCG":   "^CNXFMCG",
}


def get_market_snapshot() -> Dict[str, Any]:
    snapshot = {}
    for name, symbol in NIFTY_INDICES.items():
        try:
            fi     = yf.Ticker(symbol).fast_info
            last   = float(fi.last_price)
            prev   = float(fi.previous_close)
            change = round(((last - prev) / prev) * 100, 2) if prev else 0
            snapshot[name] = {"price": round(last, 2), "change_pct": change}
        except Exception:
            snapshot[name] = {"price": 0, "change_pct": 0}
    return snapshot


def generate_morning_briefing() -> str:
    today    = datetime.now().strftime("%A, %d %B %Y")
    snapshot = get_market_snapshot()

    market_lines = "\n".join([
        f"- {name}: ₹{v['price']:,.2f} ({'+' if v['change_pct']>=0 else ''}{v['change_pct']}%)"
        for name, v in snapshot.items()
    ])
    nifty_chg = snapshot.get("Nifty 50", {}).get("change_pct", 0)
    mood  = "BULLISH 🐂" if nifty_chg > 0.5 else "BEARISH 🐻" if nifty_chg < -0.5 else "SIDEWAYS 🦄"
    arrow = lambda c: "↑" if c >= 0 else "↓"

    prompt = f"""Generate a morning market brief for Indian retail investors.
Date: {today} | Mood: {mood}
Live NSE Data:
{market_lines}

Format:
🌅 **GOOD MORNING — Market Brief | {today}**
📊 **Market Mood**: {mood} — [1-line reason]
🔢 **Index Snapshot**: [all 6 with arrows]
🎯 **3 Things to Watch**: [numbered list]
⚡ **StockSense Signal**: [BUY DIP/HOLD/BOOK PROFITS/WAIT + reason]
⚠️ Not SEBI-registered advice. — StockSense AI | NeuralForge
Max 180 words."""

    text, model = call_llm(prompt, max_tokens=300)
    if text:
        return text

    # Rule-based fallback briefing
    index_lines = "\n".join([
        f"{arrow(v['change_pct'])} {name}: ₹{v['price']:,.2f} ({'+' if v['change_pct']>=0 else ''}{v['change_pct']}%)"
        for name, v in snapshot.items()
    ])
    signal = "BUY THE DIP 🟢" if nifty_chg < -1 else \
             "BOOK PROFITS 🔴" if nifty_chg > 1 else \
             "HOLD & WATCH 🟡"

    return f"""🌅 **GOOD MORNING — Market Brief | {today}**

📊 **Market Mood**: {mood}

🔢 **Index Snapshot**:
{index_lines}

🎯 **3 Things to Watch**:
1. Nifty 50 key level: ₹{snapshot.get('Nifty 50',{}).get('price',0):,.0f}
2. Banking sector momentum — watch HDFCBANK, ICICIBANK
3. Global cues: US Fed, FII flows into India

⚡ **StockSense Signal**: {signal}

⚠️ Not SEBI-registered advice. — StockSense AI | NeuralForge"""
