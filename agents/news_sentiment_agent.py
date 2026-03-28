"""
NewsSentimentAgent — StockSense AI | NeuralForge
Gemini 2.0 Flash -> HuggingFace Mistral -> keyword rule-based fallback.
Never shows raw API errors to the UI.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yfinance as yf
from datetime import datetime
from typing import Dict, Any, List
from agents.llm_router import call_llm   # compatibility alias — always safe to import


def fetch_stock_news(ticker: str) -> List[Dict]:
    nse = ticker.upper()
    if not nse.endswith(".NS"):
        nse += ".NS"
    try:
        news   = yf.Ticker(nse).news or []
        result = []
        for item in news[:8]:
            t     = item.get("providerPublishTime", 0)
            title = item.get("title", "").strip()
            if not title:
                continue
            result.append({
                "title":     title,
                "publisher": item.get("publisher", "Unknown"),
                "date":      datetime.fromtimestamp(t).strftime("%d %b %Y") if t else "Recent",
                "url":       item.get("link", ""),
            })
        return result
    except Exception:
        return []


def analyze_news_sentiment(ticker: str) -> Dict[str, Any]:
    news_items   = fetch_stock_news(ticker)
    ticker_clean = ticker.upper().replace(".NS", "")

    if not news_items:
        return {
            "ticker":           ticker_clean,
            "overall_sentiment": "NEUTRAL",
            "sentiment_score":   50,
            "key_themes":        ["No recent news"],
            "analysis":          "No recent news articles found for this ticker.",
            "source_citations":  "",
            "raw_news":          [],
            "news_count":        0,
        }

    news_text = "\n".join([
        f"[{n['date']}] {n['title']} ({n['publisher']})"
        for n in news_items
    ])

    prompt = f"""Analyze the sentiment of these news headlines for {ticker_clean} (NSE India stock).

HEADLINES:
{news_text}

Reply in EXACTLY this format (no extra text):
SENTIMENT: [STRONGLY_BULLISH/BULLISH/NEUTRAL/BEARISH/STRONGLY_BEARISH]
SCORE: [0-100]
THEMES: [theme1, theme2, theme3]
ANALYSIS: [2 plain-English sentences for a retail investor]
SOURCES: [top 2 publishers]"""

    # call_llm tries Gemini first, then HuggingFace, returns (None, reason) on failure
    text, _ = call_llm(prompt, max_tokens=150)

    if text:
        parsed = {}
        for line in text.strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                parsed[k.strip()] = v.strip()
        try:
            score = int(parsed.get("SCORE", "50").replace("+", "").strip())
        except Exception:
            score = 50
        # Clamp score to 0-100
        score = max(0, min(100, score))
        return {
            "ticker":           ticker_clean,
            "overall_sentiment": parsed.get("SENTIMENT", "NEUTRAL"),
            "sentiment_score":   score,
            "key_themes":        [t.strip() for t in parsed.get("THEMES", "").split(",") if t.strip()],
            "analysis":          parsed.get("ANALYSIS", "Analysis unavailable."),
            "source_citations":  parsed.get("SOURCES", ""),
            "raw_news":          news_items,
            "news_count":        len(news_items),
        }

    # ── Rule-based fallback: keyword sentiment scoring ──────────────────
    bullish_kw = ["profit","growth","buy","upgrade","outperform","record","beat","surge","rally","strong","win","expand"]
    bearish_kw = ["loss","decline","sell","downgrade","underperform","miss","drop","weak","cut","fall","fraud","probe"]
    all_text   = " ".join(n["title"].lower() for n in news_items)
    b_score    = sum(1 for w in bullish_kw if w in all_text)
    s_score    = sum(1 for w in bearish_kw if w in all_text)
    sentiment  = "BULLISH" if b_score > s_score else "BEARISH" if s_score > b_score else "NEUTRAL"
    score_val  = min(100, max(0, 50 + (b_score - s_score) * 8))

    return {
        "ticker":           ticker_clean,
        "overall_sentiment": sentiment,
        "sentiment_score":   score_val,
        "key_themes":        ["Keyword-based analysis", f"{b_score} bullish signals", f"{s_score} bearish signals"],
        "analysis":          f"{len(news_items)} recent articles found. Sentiment: {sentiment} (keyword engine).",
        "source_citations":  ", ".join(set(n["publisher"] for n in news_items[:3])),
        "raw_news":          news_items,
        "news_count":        len(news_items),
    }
