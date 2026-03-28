"""
ExplanationAgent — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026
Synthesizes outputs from all agents into plain-English brief using Gemini.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any

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


def generate_market_explanation(
    pattern_data: Dict[str, Any],
    signal_data: Dict[str, Any],
    news_data: Dict[str, Any] = None
) -> str:
    _configure_gemini()

    ticker       = pattern_data.get("ticker", "this stock")
    price        = pattern_data.get("current_price", "N/A")
    change_1d    = pattern_data.get("price_change_1d", 0)
    company      = signal_data.get("company_name", ticker)
    sector       = signal_data.get("sector", "N/A")
    fundamentals = signal_data.get("fundamentals", {})

    patterns_text = "\n".join([
        f"- {p['pattern']} ({int(p['confidence']*100)}%, {p['signal']}): {p.get('detail','')}"
        for p in pattern_data.get("patterns", [])
    ])
    signals_text = "\n".join([
        f"- [{s['strength']}] {s['signal_type']}: {s['message']}"
        for s in signal_data.get("signals", [])
    ])
    news_context = ""
    if news_data:
        news_context = (
            f"\nNEWS SENTIMENT: {news_data.get('overall_sentiment','NEUTRAL')} "
            f"(Score: {news_data.get('sentiment_score',50)}/100)\n"
            f"Key Themes: {', '.join(news_data.get('key_themes',[]))}\n"
            f"Analysis: {news_data.get('analysis','')}"
        )

    prompt = f"""You are StockSense AI — expert Indian stock market analyst.
Write a clear, actionable market brief for a retail investor.

STOCK: {company} ({ticker}) | Price: ₹{price} | 1D Change: {change_1d}%
Sector: {sector} | P/E: {fundamentals.get('pe_ratio','N/A')} | 52W High: ₹{fundamentals.get('52w_high','N/A')} | 52W Low: ₹{fundamentals.get('52w_low','N/A')}
{news_context}
TECHNICAL PATTERNS:
{patterns_text}

OPPORTUNITY SIGNALS:
{signals_text}

Write in EXACTLY this format:
## 📊 Market Brief: {ticker}
[2 sentences: what is happening right now]

## 🔍 What the Charts Say
[Plain-English explanation of patterns. No jargon.]

## 💡 Key Opportunity / Risk
[Single most important thing to know today]

## ✅ Suggested Action
[BUY / HOLD / SELL / WATCH — with a clear condition]

## ⚠️ Disclaimer
StockSense AI is for educational purposes only. Not SEBI-registered advice.
Always consult a SEBI-registered advisor before investing.

Tone: Confident, simple, under 300 words. Use ₹ for Indian currency."""

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        return model.generate_content(prompt).text
    except Exception as e:
        return f"""## 📊 Market Brief: {ticker}

AI analysis temporarily unavailable: {str(e)}

## ⚠️ Disclaimer
Not SEBI-registered investment advice. Do your own research."""


if __name__ == "__main__":
    print(generate_market_explanation(
        {"ticker":"RELIANCE","current_price":2847,"price_change_1d":1.2,
         "patterns":[{"pattern":"MACD Bullish Crossover","confidence":0.82,"signal":"BULLISH","detail":"Momentum up"}]},
        {"company_name":"Reliance Industries","sector":"Energy",
         "signals":[{"signal_type":"UNDERVALUATION","strength":"HIGH","message":"P/E below 15"}],
         "fundamentals":{"pe_ratio":12.5}}
    ))
