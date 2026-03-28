"""
PortfolioChatAgent — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026
Portfolio-aware AI chat with source citations using Gemini.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

GEMINI_MODEL = "gemini-2.0-flash"


def _configure_gemini():
    try:
        import streamlit as st
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    except Exception:
        api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)


def format_portfolio_context(portfolio: List[Dict]) -> str:
    if not portfolio:
        return "No portfolio holdings provided."
    lines = ["User's Portfolio:"]
    total = 0
    for h in portfolio:
        val = h.get("qty", 0) * h.get("avg_price", 0)
        total += val
        lines.append(
            f"  - {h.get('ticker','?')}: {h.get('qty',0)} shares "
            f"@ ₹{h.get('avg_price',0):.2f} avg → ₹{val:,.0f}"
        )
    lines.append(f"  Total invested: ₹{total:,.0f}")
    return "\n".join(lines)


def portfolio_chat(
    user_message: str,
    portfolio: List[Dict] = None,
    chat_history: List[Dict] = None,
) -> str:
    _configure_gemini()
    portfolio    = portfolio or []
    chat_history = chat_history or []

    history_ctx = ""
    if chat_history:
        recent = chat_history[-4:]
        history_ctx = "\nPrevious conversation:\n" + "\n".join(
            f"{m['role'].upper()}: {m['content'][:200]}" for m in recent
        )

    system_prompt = f"""You are StockSense AI — an intelligent Indian stock market assistant for ET Markets.

{format_portfolio_context(portfolio)}
{history_ctx}

Rules:
1. Be portfolio-aware — reference holdings when relevant
2. Cite data sources (NSE fundamentals, technical indicators, news sentiment)
3. Use Indian context — ₹, NSE/BSE, SEBI, Nifty 50
4. Give actionable insight for specific stocks
5. Flag portfolio risks proactively
6. Under 250 words. Clear and scannable.
7. End with: ⚠️ Disclaimer: Not SEBI-registered advice.

User: {user_message}

StockSense AI:"""

    try:
        return genai.GenerativeModel(GEMINI_MODEL).generate_content(system_prompt).text
    except Exception as e:
        return (
            f"Connection issue: {str(e)}\n\n"
            f"⚠️ Disclaimer: Not SEBI-registered investment advice."
        )


if __name__ == "__main__":
    print(portfolio_chat(
        "Which of my stocks has highest risk?",
        [{"ticker":"RELIANCE","qty":10,"avg_price":2800},
         {"ticker":"INFY",   "qty":20,"avg_price":1500}]
    ))
