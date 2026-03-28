"""
PortfolioChatAgent — StockSense AI | NeuralForge
Gemini 2.0 Flash -> HuggingFace Mistral -> Offline rule-based.
Never shows raw API errors. Always returns a useful response.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Dict, Any, List
from agents.llm_router import call_gemini, call_huggingface


def format_portfolio_context(portfolio: List[Dict]) -> str:
    if not portfolio:
        return "No portfolio provided."
    lines  = ["User Portfolio (NSE Holdings):"]
    total  = 0
    for h in portfolio:
        val = h.get("qty", 0) * h.get("avg_price", 0)
        total += val
        lines.append(f"  - {h.get('ticker','?')}: {h.get('qty',0)} shares @ \u20b9{h.get('avg_price',0):.0f} = \u20b9{val:,.0f}")
    lines.append(f"  Total invested: \u20b9{total:,.0f}")
    return "\n".join(lines)


def _offline_chat(user_message: str, portfolio: List[Dict]) -> str:
    """Always-works structured response. No LLM needed."""
    msg_lower = user_message.lower()

    if portfolio:
        holdings  = ", ".join(h["ticker"] for h in portfolio)
        total_val = sum(h["qty"] * h["avg_price"] for h in portfolio)
        port_ctx  = f"Your portfolio: **{holdings}** | Total: **\u20b9{total_val:,.0f}**"
    else:
        port_ctx = "No portfolio added. Use the sidebar to add your NSE holdings."

    if any(w in msg_lower for w in ["defensive", "correction", "bear", "protect", "safe"]):
        advice = """**Defensive Strategy for Market Correction:**

\U0001f4b9 **Safe Haven Sectors:**
- **FMCG**: HUL (HINDUNILVR), ITC, Nestle \u2014 demand stays in corrections
- **Pharma**: Sun Pharma (SUNPHARMA), Cipla \u2014 recession-proof
- **Utilities**: NTPC, Power Grid \u2014 stable dividends, low beta

\U0001f6e1\ufe0f **Portfolio Protection Moves:**
1. Trim high-beta IT/Auto by 20-30%
2. Raise cash allocation to 15-20%
3. Add gold ETF for 5-10% hedge
4. Keep SIP running \u2014 corrections = cheaper NAV

\U0001f4ca **Nifty Support**: 22,000 \u2014 22,500 is key zone to watch"""
    elif any(w in msg_lower for w in ["buy", "invest", "entry", "accumulate"]):
        advice = """**Entry Strategy in Current Market:**

\U0001f3af **High-Conviction Picks (Staggered Entry):**
- **Reliance** (RELIANCE): Core holding, diversified biz
- **HDFC Bank** (HDFCBANK): Strongest private bank, fair value zone
- **Infosys** (INFY): IT bellwether, watch Q4 guidance

\U0001f4b0 **Entry Style:**
1. Don\u2019t go all-in \u2014 buy in 3 tranches over 3 weeks
2. Set stop-loss at 8-10% below entry
3. Target 12-18 month horizon for full returns"""
    elif any(w in msg_lower for w in ["sell", "exit", "book", "profit"]):
        advice = """**Profit Booking / Exit Strategy:**

\U0001f4c9 **When to Exit:**
- Stock has run up 40%+ without fundamental improvement
- P/E is above 5-year average by 20%+
- Sector headwinds (RBI rate hikes, global slowdown)

\u2705 **Rule of Thumb:**
- Book 30-50% at first target, let rest run
- Never exit fundamentally strong businesses in corrections
- Tax-loss harvesting: offset STCG with loss-making positions"""
    elif any(w in msg_lower for w in ["it", "tech", "software", "infy", "tcs", "wipro"]):
        advice = """**IT Sector Outlook:**

\U0001f4bb **Current View**: NEUTRAL to CAUTIOUS
- US recession fears = demand slowdown for Indian IT
- Rupee depreciation = partial revenue hedge for exporters
- Q4 results season: Watch TCS, Infosys guidance carefully

\U0001f3af **Plays**: HCLTECH showing relative strength | TECHM underperforming
- Wait for Q4 commentary before fresh IT positions"""
    else:
        advice = """**General Market Guidance:**

\U0001f4ca **Current Market Snapshot:**
- Nifty in corrective phase \u2014 support zone 22,000-22,500
- Broader market (Midcap/Smallcap) under pressure
- FII selling = short-term headwind

\U0001f3af **Strategy:**
1. Continue SIPs \u2014 don\u2019t pause during corrections
2. Avoid leveraged/F&O positions in uncertain markets
3. Watch: FII flows, RBI policy, US Fed commentary
4. Next major trigger: Q4 earnings season (April)"""

    return f"""**StockSense AI Analysis**

{port_ctx}

{advice}

\u26a0\ufe0f Not SEBI-registered advice. Always consult a SEBI-registered advisor before investing.
*\u2699\ufe0f Powered by StockSense AI rule engine \u00b7 Team NeuralForge*"""


def portfolio_chat(
    user_message:  str,
    portfolio:     List[Dict] = None,
    chat_history:  List[Dict] = None,
) -> str:
    portfolio    = portfolio    or []
    chat_history = chat_history or []

    history_ctx = ""
    if chat_history:
        history_ctx = "\nRecent conversation:\n" + "\n".join(
            f"{m['role'].upper()}: {m['content'][:150]}"
            for m in chat_history[-3:]
        )

    prompt = f"""You are StockSense AI \u2014 India's expert stock market assistant built for ET Markets.

{format_portfolio_context(portfolio)}
{history_ctx}

User asks: {user_message}

Instructions:
- Be portfolio-aware and specific to the user's holdings
- Use \u20b9 and Indian context (NSE/BSE/SEBI/Nifty/Sensex)
- Give actionable, source-cited advice under 200 words
- Use markdown bold for key points
- End every response with: \u26a0\ufe0f Not SEBI-registered advice.

StockSense AI Response:"""

    # Tier 1: Gemini
    try:
        text, src = call_gemini(prompt)
        if text and len(text) > 80:
            return text + "\n\n*\U0001f916 Powered by Gemini 2.0 Flash \u00b7 StockSense AI*"
    except Exception:
        pass

    # Tier 2: HuggingFace
    try:
        text, src = call_huggingface(prompt)
        if text and len(text) > 80:
            return text + "\n\n*\U0001f916 Powered by HuggingFace Mistral \u00b7 StockSense AI*"
    except Exception:
        pass

    # Tier 3: Offline (always works)
    return _offline_chat(user_message, portfolio)
