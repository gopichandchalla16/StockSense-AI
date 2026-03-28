# 📈 StockSense AI — Multi-Agent NSE Intelligence

> **Team NeuralForge** | ET GenAI Hackathon 2026 | Problem Statement #6 — AI for the Indian Investor



StockSense AI is a **7-agent GenAI system** that turns India's NSE market data into actionable intelligence for 14 crore+ retail investors — combining real-time chart pattern detection, opportunity radar, FII/DII smart money tracking, IPO intelligence, news sentiment analysis, and portfolio-aware AI chat.

---

## 🤖 7-Agent Architecture

```
User Input (NSE Ticker)
        ↓
[PatternDetectorAgent]  →  yfinance + pandas-ta  →  chart patterns + confidence
        ↓
[SignalFinderAgent]     →  NSE fundamentals      →  opportunity signals
        ↓
[NewsSentimentAgent]   →  yfinance news + Gemini →  source-cited sentiment
        ↓
[ExplanationAgent]     →  Gemini 1.5 Flash       →  plain-English market brief
        ↓
[FIIDIIAgent]          →  NSE public API         →  smart money flow signals
        ↓
[IPOIntelligenceAgent] →  NSE IPO API + Gemini   →  buy/avoid verdict per IPO
        ↓
[PortfolioChatAgent]   →  Gemini + context       →  portfolio-aware Q&A
        ↓
   Orchestrated by LangGraph StateGraph with full audit trail
```

---

## 🚀 Live Demo

👉 **[StockSense AI — Live App](https://stocksense-ai.streamlit.app)**

---

## ✨ Features

| Feature | Sub-Problem Solved |
|---|---|
| 📊 Chart Pattern Intelligence | RSI, MACD, Golden/Death Cross, Bollinger Bands |
| 🎯 Opportunity Radar | P/E signals, 52-week proximity, dividend alerts |
| 📰 News Sentiment Analysis | Source-cited, Gemini-powered, 8 headlines analyzed |
| 🏦 FII/DII Smart Money Tracker | Live institutional flow from NSE India |
| 🚀 IPO Intelligence Center | AI verdict (Subscribe/Avoid) per upcoming IPO |
| 🌡️ NSE Sector Heatmap | Live Plotly Treemap — green/red by % change |
| 🏎️ Race Chart Engine | Animated Nifty Top-10 performance bar race |
| 🌅 Morning Briefing Engine | Auto-generated daily market brief on app load |
| 💬 Portfolio Chat | Multi-step, portfolio-aware, source-cited answers |

---

## 🛠️ Tech Stack

| Tool | Purpose | Cost |
|---|---|---|
| LangGraph | Multi-agent orchestration | Free |
| LangChain | Agent tooling | Free |
| yfinance | NSE/BSE live data + news | Free |
| pandas-ta | 50+ technical indicators | Free |
| Google Gemini 1.5 Flash | LLM (1M tokens/day) | Free |
| Streamlit | Web UI + deployment | Free |
| Plotly | Interactive charts | Free |
| FAISS | Vector search | Free |
| NSE India API | FII/DII + bulk deals | Free |

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
# Add your free Gemini API key from: https://aistudio.google.com/app/apikey

# 4. Run the app
streamlit run ui/streamlit_app.py
```

---

## 📁 Project Structure

```
StockSense-AI/
├── agents/
│   ├── pattern_agent.py        ← PatternDetectorAgent
│   ├── signal_agent.py         ← SignalFinderAgent
│   ├── news_sentiment_agent.py ← NewsSentimentAgent
│   ├── fii_dii_agent.py        ← FIIDIIAgent
│   ├── ipo_agent.py            ← IPOIntelligenceAgent
│   ├── explanation_agent.py    ← ExplanationAgent
│   ├── portfolio_chat.py       ← PortfolioChatAgent
│   └── morning_briefing.py     ← MorningBriefingEngine
├── orchestrator/
│   └── langgraph_flow.py       ← LangGraph StateGraph
├── ui/
│   ├── streamlit_app.py        ← Main 6-tab Streamlit UI
│   └── charts/
│       ├── sector_heatmap.py   ← NSE Sector Treemap
│       └── race_chart.py       ← Animated Bar Race Chart
├── docs/
│   └── architecture.md         ← System architecture diagram
├── impact_model.md             ← Business impact calculations
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

## 🏗️ Architecture

See [`docs/architecture.md`](docs/architecture.md) for full multi-agent flow diagram and agent communication details.

---

## ⚠️ Disclaimer

StockSense AI is for educational purposes only. Not SEBI-registered investment advice. Always do your own research before investing.

---

## 👥 Team NeuralForge

**Lead Engineer:** Challa Gopichand  
**Hackathon:** ET GenAI Hackathon 2026  
**Problem Statement:** #6 — AI for the Indian Investor
