"""
PortfolioChatAgent — StockSense AI | NeuralForge
Gemini 2.0 Flash → HuggingFace → rule-based fallback.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Dict, Any, List
from agents.llm_router import call_llm


def format_portfolio_context(portfolio: List[Dict]) -> str:
    if not portfolio:
        return "No portfolio provided."
    lines = ["User Portfolio:"]
    total = 0
    for h in portfolio:
        val = h.get("qty", 0) * h.get("avg_price", 0)
        total += val
        lines.append(f"  {h.get('ticker','?')}: {h.get('qty',0)} shares @ ₹{h.get('avg_price',0):.0f} = ₹{val:,.0f}")
    lines.append(f"  Total: ₹{total:,.0f}")
    return "\n".join(lines)


def portfolio_chat(
    user_message: str,
    portfolio: List[Dict] = None,
    chat_history: List[Dict] = None,
) -> str:
    portfolio    = portfolio or []
    chat_history = chat_history or []

    history_ctx = ""
    if chat_history:
        history_ctx = "\nRecent chat:\n" + "\n".join(
            f"{m['role'].upper()}: {m['content'][:150]}" for m in chat_history[-3:]
        )

    prompt = f"""You are StockSense AI — an expert Indian stock market assistant for ET Markets / ET GenAI Hackathon.

{format_portfolio_context(portfolio)}
{history_ctx}

User asks: {user_message}

Rules: Be portfolio-aware. Cite sources. Use ₹ and Indian context (NSE/BSE/SEBI/Nifty).
Give actionable, specific advice. Under 200 words.
End with: ⚠️ Not SEBI-registered advice.

StockSense AI:"""

    text, model = call_llm(prompt, max_tokens=300)
    if text:
        return text

    # Fallback: smart rule-based response
    if portfolio:
        holdings = ", ".join(h["ticker"] for h in portfolio)
        total    = sum(h["qty"] * h["avg_price"] for h in portfolio)
        return f"""**StockSense AI Analysis** (offline mode)

Your portfolio: **{holdings}** | Total invested: **₹{total:,.0f}**

For your question: *"{user_message}"*

With current market conditions (Nifty -2.1%), I recommend:
- **Defensive holdings** (ITC, FMCG, Pharma) tend to hold up better
- **IT sector** (INFY, TCS, WIPRO) facing global headwinds — watch Q4 results
- Keep **SIP discipline** — market corrections are long-term buying opportunities
- **Avoid panic selling** — review fundamentals before any exit

⚠️ Not SEBI-registered advice. Always consult a SEBI-registered advisor."""
    else:
        return f"""**StockSense AI** (offline mode)

For: *"{user_message}"*

General market guidance:
- Indian markets are currently in a **corrective phase** — Nifty support at 22,000-22,500
- **Pharma + FMCG** sectors showing relative strength
- **IT sector** watch earnings season — guidance will set tone
- **SIP investors**: Continue — corrections are opportunities
- **Traders**: Wait for clear reversal signals before new positions

⚠️ Not SEBI-registered advice. Add your portfolio in sidebar for personalized analysis."""
