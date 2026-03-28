"""
NewsSentimentAgent — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026

Fetches news via yfinance and analyzes sentiment using Gemini 1.5 Flash.
Always returns source-cited responses.
"""

import os
import yfinance as yf
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
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
    return api_key


def fetch_stock_news(ticker: str) -> List[Dict]:
    """Fetch recent news headlines for a NSE ticker via yfinance (free)."""
    nse_ticker = ticker.upper() + ".NS" if not ticker.upper().endswith(".NS") else ticker.upper()
    try:
        stock = yf.Ticker(nse_ticker)
        news = stock.news
        cleaned = []
        for item in (news or [])[:8]:
            pub_time = item.get("providerPublishTime", 0)
            date_str = datetime.fromtimestamp(pub_time).strftime("%d %b %Y") if pub_time else "Recent"
            cleaned.append({
                "title": item.get("title", "No title"),
                "publisher": item.get("publisher", "Unknown"),
                "date": date_str,
                "url": item.get("link", "")
            })
        return cleaned
    except Exception as e:
        print(f"[NewsSentimentAgent] News fetch error: {e}")
        return []


def analyze_news_sentiment(ticker: str) -> Dict[str, Any]:
    """
    Analyze news sentiment for a NSE ticker using Gemini 1.5 Flash.
    Returns structured sentiment with source citations.
    """
    _configure_gemini()
    news_items = fetch_stock_news(ticker)
    ticker_clean = ticker.upper().replace(".NS", "")

    if not news_items:
        return {
            "ticker": ticker_clean,
            "overall_sentiment": "NEUTRAL",
            "sentiment_score": 50,
            "key_themes": ["No recent news found"],
            "analysis": "No recent news articles found for this ticker. This could indicate low media coverage or a data gap.",
            "source_citations": "",
            "raw_news": [],
            "news_count": 0
        }

    news_text = "\n".join([
        f"- [{n['date']}] {n['title']} (Source: {n['publisher']})"
        for n in news_items
    ])

    prompt = f"""Analyze the following recent news headlines for {ticker_clean} (NSE-listed Indian company).

NEWS HEADLINES:
{news_text}

Provide structured analysis for a retail investor. Reply in EXACTLY this format:
SENTIMENT: [STRONGLY_BULLISH / BULLISH / NEUTRAL / BEARISH / STRONGLY_BEARISH]
SCORE: [0-100 where 100 is most bullish]
THEMES: [3 key themes, comma-separated]
ANALYSIS: [2 sentences in plain English — what does this news mean for investors?]
SOURCES: [top 2 publishers cited]

Be factual. Use Indian market context. Avoid jargon."""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()

        parsed = {}
        for line in text.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                parsed[key.strip()] = val.strip()

        return {
            "ticker": ticker_clean,
            "overall_sentiment": parsed.get("SENTIMENT", "NEUTRAL"),
            "sentiment_score": int(parsed.get("SCORE", "50").replace("+", "").strip()),
            "key_themes": [t.strip() for t in parsed.get("THEMES", "").split(",") if t.strip()],
            "analysis": parsed.get("ANALYSIS", "Analysis unavailable."),
            "source_citations": parsed.get("SOURCES", ""),
            "raw_news": news_items,
            "news_count": len(news_items)
        }
    except Exception as e:
        return {
            "ticker": ticker_clean,
            "overall_sentiment": "NEUTRAL",
            "sentiment_score": 50,
            "key_themes": ["Analysis error"],
            "analysis": f"Gemini analysis temporarily unavailable: {str(e)}",
            "source_citations": "",
            "raw_news": news_items,
            "news_count": len(news_items)
        }


if __name__ == "__main__":
    print("Testing NewsSentimentAgent with TCS...")
    result = analyze_news_sentiment("TCS")
    print(f"Sentiment: {result['overall_sentiment']} (Score: {result['sentiment_score']}/100)")
    print(f"Themes: {result['key_themes']}")
    print(f"Analysis: {result['analysis']}")
