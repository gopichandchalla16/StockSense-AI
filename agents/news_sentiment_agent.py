"""
NewsSentimentAgent — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026
Fetches news via yfinance and analyzes sentiment using Gemini.
"""
import os
import yfinance as yf
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
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


def fetch_stock_news(ticker: str) -> List[Dict]:
    nse = ticker.upper()
    if not nse.endswith(".NS"):
        nse += ".NS"
    try:
        news = yf.Ticker(nse).news or []
        cleaned = []
        for item in news[:8]:
            t = item.get("providerPublishTime", 0)
            cleaned.append({
                "title":     item.get("title", ""),
                "publisher": item.get("publisher", "Unknown"),
                "date":      datetime.fromtimestamp(t).strftime("%d %b %Y") if t else "Recent",
                "url":       item.get("link", ""),
            })
        return cleaned
    except Exception:
        return []


def analyze_news_sentiment(ticker: str) -> Dict[str, Any]:
    _configure_gemini()
    news_items  = fetch_stock_news(ticker)
    ticker_clean = ticker.upper().replace(".NS", "")

    if not news_items:
        return {
            "ticker": ticker_clean, "overall_sentiment": "NEUTRAL",
            "sentiment_score": 50, "key_themes": ["No recent news"],
            "analysis": "No recent news found for this ticker.",
            "source_citations": "", "raw_news": [], "news_count": 0,
        }

    news_text = "\n".join([
        f"- [{n['date']}] {n['title']} (Source: {n['publisher']})"
        for n in news_items
    ])

    prompt = f"""Analyze news headlines for {ticker_clean} (NSE India).

NEWS:
{news_text}

Reply in EXACTLY this format:
SENTIMENT: [STRONGLY_BULLISH / BULLISH / NEUTRAL / BEARISH / STRONGLY_BEARISH]
SCORE: [0-100]
THEMES: [theme1, theme2, theme3]
ANALYSIS: [2-sentence plain English for retail investor]
SOURCES: [top 2 publishers]"""

    try:
        resp = genai.GenerativeModel(GEMINI_MODEL).generate_content(prompt)
        parsed = {}
        for line in resp.text.strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                parsed[k.strip()] = v.strip()
        return {
            "ticker": ticker_clean,
            "overall_sentiment": parsed.get("SENTIMENT", "NEUTRAL"),
            "sentiment_score":   int(parsed.get("SCORE", "50").replace("+","").strip()),
            "key_themes":        [t.strip() for t in parsed.get("THEMES","").split(",") if t.strip()],
            "analysis":          parsed.get("ANALYSIS", "Analysis unavailable."),
            "source_citations":  parsed.get("SOURCES", ""),
            "raw_news":          news_items,
            "news_count":        len(news_items),
        }
    except Exception as e:
        return {
            "ticker": ticker_clean, "overall_sentiment": "NEUTRAL",
            "sentiment_score": 50, "key_themes": [],
            "analysis": f"Gemini unavailable: {str(e)}",
            "source_citations": "", "raw_news": news_items,
            "news_count": len(news_items),
        }


if __name__ == "__main__":
    r = analyze_news_sentiment("TCS")
    print(f"{r['overall_sentiment']} ({r['sentiment_score']}/100): {r['analysis']}")
