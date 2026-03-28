# 📈 StockSense AI — Multi-Agent NSE Intelligence Platform

> **Team NeuralForge** | ET GenAI Hackathon 2026 | Problem Statement #6 — AI for the Indian Investor

---

## 🚀 Live Demo

<div align="center">

### 👉 [**stocksense-neuralforge.streamlit.app**](https://stocksense-neuralforge.streamlit.app/)

[![Live App](https://img.shields.io/badge/🚀%20Live%20App-StockSense%20AI-00d4ff?style=for-the-badge)](https://stocksense-neuralforge.streamlit.app/)
[![Hackathon](https://img.shields.io/badge/🏆%20ET%20GenAI-Hackathon%202026-7b2ff7?style=for-the-badge)](https://stocksense-neuralforge.streamlit.app/)
[![NSE Live](https://img.shields.io/badge/📡%20NSE-LIVE%20DATA-00ff88?style=for-the-badge)](https://stocksense-neuralforge.streamlit.app/)

</div>

---

StockSense AI is a **7-agent GenAI system** that turns India's NSE market data into actionable intelligence for 14 crore+ retail investors — combining real-time chart pattern detection, opportunity radar, FII/DII smart money tracking, IPO intelligence, news sentiment analysis, and portfolio-aware AI chat.

**3-Tier Resilient LLM**: Gemini 2.0 Flash → HuggingFace Mistral-7B → Offline Rule Engine (always works, zero downtime)

---

## 🤖 7-Agent Architecture

```
User Input (NSE Ticker / Company Name)
        ↓
[PatternDetectorAgent]  →  yfinance + pandas-ta    →  RSI, MACD, Bollinger, EMA patterns
        ↓
[SignalFinderAgent]     →  NSE fundamentals         →  P/E signals, 52W alerts, div yield
        ↓
[NewsSentimentAgent]   →  yfinance news + Gemini   →  source-cited sentiment (8 headlines)
        ↓
[ExplanationAgent]     →  Gemini 2.0 Flash         →  plain-English AI market brief
        ↓
[FIIDIIAgent]          →  NSE public API            →  smart money flow signals
        ↓
[IPOIntelligenceAgent] →  NSE IPO API + Gemini     →  subscribe/avoid verdict per IPO
        ↓
[PortfolioChatAgent]   →  Gemini → Mistral → Rules →  portfolio-aware Q&A
        ↓
   Orchestrated by LangGraph StateGraph with full audit trail
```

---

## ✨ Features

| Feature | Sub-Problem Solved | Status |
|---|---|---|
| 📊 Chart Pattern Intelligence | RSI, MACD, Golden/Death Cross, Bollinger Bands | ✅ Live |
| 🎯 Opportunity Radar | P/E signals, 52W proximity, dividend alerts | ✅ Live |
| 📰 News Sentiment Analysis | Source-cited, Gemini-powered, 8 headlines | ✅ Live |
| 🏦 FII/DII Smart Money Tracker | Live institutional flow from NSE India | ✅ Live |
| 🚀 IPO Intelligence Center | AI verdict (Subscribe/Avoid) per upcoming IPO | ✅ Live |
| 🌡️ NSE Sector Heatmap | Live Plotly Treemap — 40 stocks, 8 sectors | ✅ Live |
| 📊 Sector Bar Chart | 8-sector performance ranking bar chart | ✅ Live |
| 🔥 Top Movers Chart | Top 5 gainers vs losers — today | ✅ Live |
| 🏎️ Race Chart Engine | Animated Nifty Top-10 performance bar race | ✅ Live |
| 🌅 Morning Briefing Engine | Auto-generated daily AI market brief | ✅ Live |
| 💬 Portfolio Chat | Multi-step, portfolio-aware, source-cited Q&A | ✅ Live |

---

## 🛡️ Resilient LLM Architecture (Zero Downtime)

```
Tier 1: Gemini 2.0 Flash      → Best quality, fastest
    ↓ (if quota exceeded / error)
Tier 2: HuggingFace Mistral-7B → Free fallback, no API key needed
    ↓ (if both fail)
Tier 3: Offline Rule Engine    → Always works, structured analysis
                                  NO blank pages. EVER.
```

---

## 🛠️ Tech Stack

| Tool | Purpose | Cost |
|---|---|---|
| LangGraph | Multi-agent orchestration | Free |
| LangChain | Agent tooling | Free |
| yfinance | NSE/BSE live data + news | Free |
| pandas-ta | 50+ technical indicators | Free |
| Google Gemini 2.0 Flash | LLM Tier 1 | Free |
| HuggingFace Mistral-7B | LLM Tier 2 fallback | Free |
| Streamlit | Web UI + Cloud deployment | Free |
| Plotly | Interactive charts (Treemap, Candlestick, Bar Race) | Free |
| NSE India API | FII/DII + IPO data | Free |

**Total infrastructure cost: ₹0**

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/gopichandchalla16/StockSense-AI
cd StockSense-AI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Add your free Gemini API key: https://aistudio.google.com/app/apikey

# 4. Run the app
streamlit run ui/streamlit_app.py
```

### Streamlit Cloud Secrets
Add these in your Streamlit Cloud → App Settings → Secrets:
```toml
GOOGLE_API_KEY = "your-gemini-api-key"
HF_TOKEN = "your-huggingface-token"   # optional
```

---

## 📁 Project Structure

```
StockSense-AI/
├── agents/
│   ├── pattern_agent.py        ← PatternDetectorAgent (RSI, MACD, BB, EMA)
│   ├── signal_agent.py         ← SignalFinderAgent (P/E, 52W, dividends)
│   ├── news_sentiment_agent.py ← NewsSentimentAgent (Gemini + keyword fallback)
│   ├── fii_dii_agent.py        ← FIIDIIAgent (NSE institutional flows)
│   ├── ipo_agent.py            ← IPOIntelligenceAgent (subscribe/avoid verdict)
│   ├── explanation_agent.py    ← ExplanationAgent (AI brief generator)
│   ├── portfolio_chat.py       ← PortfolioChatAgent (context-aware Q&A)
│   ├── morning_briefing.py     ← MorningBriefingEngine (daily market brief)
│   └── llm_router.py           ← 3-Tier LLM Router (Gemini → HF → Offline)
├── orchestrator/
│   └── langgraph_flow.py       ← LangGraph StateGraph orchestrator
├── ui/
│   ├── streamlit_app.py        ← Main 6-tab Streamlit UI
│   └── charts/
│       ├── sector_heatmap.py   ← NSE Treemap + Bar Chart + Top Movers
│       └── race_chart.py       ← Animated Bar Race Chart
├── utils/
│   └── ticker_resolver.py      ← Company name → NSE ticker resolver
├── docs/
│   └── architecture.md
├── requirements.txt
├── .env.example
└── README.md
```

---

## 💥 Business Impact

India has **14 crore+ demat accounts**. If 5% (70 lakh users) use StockSense AI:

| Metric | Value |
|---|---|
| Daily time saved per user | 40 minutes |
| Total daily hours saved | 4.67 crore hours |
| Annual wealth preservation | ₹2,499 crore |
| ET Revenue opportunity | ₹357+ crore/year |

---

## ⚠️ Disclaimer

StockSense AI is for educational purposes only. Not SEBI-registered investment advice. Always do your own research and consult a SEBI-registered advisor before investing.

---

## 👥 Team NeuralForge

**Lead Engineer:** Challa Gopichand
**Hackathon:** ET GenAI Hackathon 2026
**Problem Statement:** #6 — AI for the Indian Investor
**Live App:** [stocksense-neuralforge.streamlit.app](https://stocksense-neuralforge.streamlit.app/)
