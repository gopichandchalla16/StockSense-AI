"""
StockSense AI — Explanation Agent
Converts structured analysis → plain English AI brief.
Always returns a result via the resilient LLM router.
"""
from typing import Dict, Any
from agents.llm_router import generate_resilient_brief


def generate_market_explanation(
    pattern_data: Dict[str, Any],
    signal_data:  Dict[str, Any],
    news_data:    Dict[str, Any] = None,
) -> str:
    ticker   = pattern_data.get("ticker",        "STOCK")
    company  = signal_data.get("company_name",  ticker)
    price    = pattern_data.get("current_price", 0)
    ch1      = pattern_data.get("price_change_1d", 0)
    sector   = signal_data.get("sector",         "N/A")
    fund     = signal_data.get("fundamentals",   {})
    patterns = pattern_data.get("patterns",      [])
    signals  = signal_data.get("signals",        [])

    pattern_lines = "\n".join(
        f"- {p.get('pattern','?')} | {p.get('signal','NEUTRAL')} | {int(p.get('confidence',0.5)*100)}% confidence"
        for p in patterns[:5]
    ) or "- No strong patterns detected"

    signal_lines = "\n".join(
        f"- {s.get('signal_type','?')} | {s.get('strength','LOW')} strength | {s.get('message','')}"
        for s in signals[:5]
    ) or "- No opportunity signals"

    news_block = ""
    if news_data:
        news_block = f"""
NEWS SENTIMENT : {news_data.get('overall_sentiment','NEUTRAL')}
SENTIMENT SCORE: {news_data.get('sentiment_score',50)}/100
KEY THEMES     : {', '.join(news_data.get('key_themes',[]))}
SUMMARY        : {news_data.get('analysis','')[:300]}"""

    prompt = f"""You are StockSense AI, India's most precise stock market intelligence assistant.
Write a professional market brief for JUDGES evaluating a hackathon demo. Keep it under 200 words.
Be specific, confident, and data-driven. No fluff.

STOCK DATA
==========
Company    : {company} ({ticker}.NS)
Price      : ₹{price:,.2f}
1D Change  : {ch1:+.2f}%
Sector     : {sector}
P/E Ratio  : {fund.get('pe_ratio','N/A')}
52W High   : ₹{fund.get('52w_high','N/A')}
52W Low    : ₹{fund.get('52w_low','N/A')}
Div Yield  : {fund.get('div_yield','N/A')}%

CHART PATTERNS
==============
{pattern_lines}

OPPORTUNITY SIGNALS
===================
{signal_lines}
{news_block}

OUTPUT FORMAT (use exactly this):
## 📊 Market Brief: {ticker}
[2 sentences on current price action and momentum]

## 🔍 What the Charts Say
[1-2 sentences on strongest pattern and what it means]

## 💡 Key Opportunity / Risk
[The most important insight a retail investor must know right now]

## ✅ Suggested Action
[BUY / HOLD / SELL / WATCH — with a specific condition e.g. 'Buy above ₹X']

## ⚠️ Disclaimer
For educational purposes only. Not SEBI-registered investment advice."""

    return generate_resilient_brief(
        prompt        = prompt,
        ticker        = ticker,
        pattern_data  = pattern_data,
        signal_data   = signal_data,
        sentiment_data = news_data or {},
    )
