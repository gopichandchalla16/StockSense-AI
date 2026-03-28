"""
ExplanationAgent — StockSense AI | NeuralForge
Uses LLM Router: Gemini 2.0 Flash → HuggingFace Mistral-7B → rule-based fallback.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Dict, Any
from agents.llm_router import call_llm_with_fallback


def generate_market_explanation(
    pattern_data: Dict[str, Any],
    signal_data:  Dict[str, Any],
    news_data:    Dict[str, Any] = None
) -> str:
    ticker       = pattern_data.get("ticker", "STOCK")
    price        = pattern_data.get("current_price", "N/A")
    change_1d    = pattern_data.get("price_change_1d", 0)
    company      = signal_data.get("company_name", ticker)
    sector       = signal_data.get("sector", "N/A")
    fundamentals = signal_data.get("fundamentals", {})

    patterns_text = "\n".join([
        f"- {p['pattern']} ({int(p['confidence']*100)}%, {p['signal']}): {p.get('detail','')}"
        for p in pattern_data.get("patterns", [])
    ]) or "- No strong patterns detected"

    signals_text = "\n".join([
        f"- [{s['strength']}] {s['signal_type']}: {s['message']}"
        for s in signal_data.get("signals", [])
    ]) or "- No signals found"

    news_context = ""
    if news_data:
        news_context = (
            f"\nNEWS SENTIMENT: {news_data.get('overall_sentiment','NEUTRAL')} "
            f"({news_data.get('sentiment_score',50)}/100)\n"
            f"Themes: {', '.join(news_data.get('key_themes',[]))}\n"
            f"Analysis: {news_data.get('analysis','')}"
        )

    prompt = f"""You are StockSense AI — expert Indian stock market analyst for ET GenAI Hackathon 2026.
Write a clear, actionable market brief for a retail investor in under 300 words.

STOCK: {company} ({ticker}) | Price: ₹{price} | 1D: {change_1d}%
Sector: {sector} | P/E: {fundamentals.get('pe_ratio','N/A')} | 52W High: ₹{fundamentals.get('52w_high','N/A')} | 52W Low: ₹{fundamentals.get('52w_low','N/A')}
{news_context}
TECHNICAL PATTERNS:
{patterns_text}

OPPORTUNITY SIGNALS:
{signals_text}

Write in EXACTLY this format:
## 📊 Market Brief: {ticker}
[2 sentences: current situation]

## 🔍 What the Charts Say
[Plain-English pattern explanation]

## 💡 Key Opportunity / Risk
[Single most important insight]

## ✅ Suggested Action
[BUY / HOLD / SELL / WATCH with condition]

## ⚠️ Disclaimer
Not SEBI-registered advice. Educational only.

Tone: Confident, plain English. Use ₹."""

    return call_llm_with_fallback(prompt, ticker, pattern_data, signal_data, max_tokens=400)
