"""
PortfolioChatAgent — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026

Portfolio-aware multi-step AI chat with source citations.
Market ChatGPT Next Gen — knows your holdings and answers questions about them.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()


def _configure_gemini():
    """Configure Gemini with API key from env or Streamlit secrets."""
    try:
        import streamlit as st
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    except Exception:
        api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)


def format_portfolio_context(portfolio: List[Dict]) -> str:
    """Format portfolio holdings into readable string for Gemini context."""
    if not portfolio:
        return "No portfolio holdings provided."
    lines = ["User's Current Portfolio:"]
    total_value = 0
    for h in portfolio:
        ticker = h.get("ticker", "?")
        qty = h.get("qty", 0)
        avg = h.get("avg_price", 0)
        value = qty * avg
        total_value += value
        lines.append(f"  - {ticker}: {qty} shares @ ₹{avg:.2f} avg → ₹{value:,.0f} invested")
    lines.append(f"  Total Portfolio Value: ₹{total_value:,.0f}")
    return "\n".join(lines)


def portfolio_chat(
    user_message: str,
    portfolio: List[Dict] = None,
    chat_history: List[Dict] = None
) -> str:
    """
    Multi-step, portfolio-aware AI chat for Indian investors.
    Maintains last 4 messages as context window.
    Always includes source citations in response.
    """
    _configure_gemini()
    portfolio = portfolio or []
    chat_history = chat_history or []

    portfolio_context = format_portfolio_context(portfolio)
    history_context = ""
    if chat_history:
        recent = chat_history[-4:]  # Last 4 messages for context
        history_context = "\nPrevious conversation:\n" + "\n".join([
            f"{msg['role'].upper()}: {msg['content'][:200]}"
            for msg in recent
        ])

    system_prompt = f"""You are StockSense AI — an intelligent Indian stock market assistant
for ET Markets (Economic Times). You are knowledgeable, helpful, and always
cite your reasoning sources.

{portfolio_context}
{history_context}

Your response rules:
1. ALWAYS be portfolio-aware — if user has holdings, reference them when relevant
2. ALWAYS cite your data sources (e.g., "Based on NSE fundamentals...", "According to technical indicators...")
3. Use Indian market context — ₹, NSE/BSE, SEBI, Nifty 50, Sensex
4. If asked about a specific stock, give actionable insight (not generic advice)
5. If you detect a portfolio risk, flag it proactively
6. Keep responses under 250 words — clear, structured, and scannable
7. End every response with: ⚠️ Disclaimer: Not SEBI-registered advice.

User's question: {user_message}

Respond now as StockSense AI:"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(system_prompt)
        return response.text
    except Exception as e:
        return f"""I\'m having trouble connecting right now ({str(e)}).

For your portfolio of {len(portfolio)} stocks, please try again in a moment.

⚠️ Disclaimer: Not SEBI-registered investment advice."""


if __name__ == "__main__":
    test_portfolio = [
        {"ticker": "RELIANCE", "qty": 10, "avg_price": 2800.0},
        {"ticker": "INFY", "qty": 20, "avg_price": 1500.0}
    ]
    print("Testing PortfolioChatAgent...")
    response = portfolio_chat(
        "Which of my stocks has the highest risk right now?",
        test_portfolio
    )
    print(response)
