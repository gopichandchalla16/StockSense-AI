# StockSense AI — System Architecture
**Team NeuralForge | ET GenAI Hackathon 2026 | PS #6**

---

## Multi-Agent LangGraph Flow

```
┌────────────────────────────────────────────────────┐
│                    USER INPUT                        │
│              (NSE Ticker Symbol)                     │
└──────────────────────┤───────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────┐
│           LANGGRAPH STATE MACHINE                    │
│         orchestrator/langgraph_flow.py               │
│                                                      │
│  AgentState {                                        │
│    ticker, pattern_data, signal_data,                │
│    sentiment_data, explanation,                      │
│    error, step_log[]                                 │
│  }                                                   │
└──────────────────────┤───────────────────────────┘
                       │
          ┌───────────┴────────────┐
          ▼                           ▼ (on error)
┌─────────────────┐              [END]
│ PatternDetector │
│    Agent        │
│ ─────────────── │
│ yfinance OHLCV  │
│ pandas-ta       │
│ RSI,MACD,Golden │
│ Cross,BBands,EMA│
└────────┼────────┘
         │
         ▼
┌─────────────────┐
│  SignalFinder   │
│    Agent        │
│ ─────────────── │
│ yfinance .info  │
│ NSE Bulk Deals  │
│ P/E, 52W, Yield │
└────────┼────────┘
         │
         ▼
┌─────────────────┐
│  Sentiment      │
│    Agent        │
│ ─────────────── │
│ yfinance .news  │
│ Gemini 1.5 Flash│
│ Source-cited    │
└────────┼────────┘
         │
         ▼
┌─────────────────┐
│  Explanation    │
│    Agent        │
│ ─────────────── │
│ Gemini 1.5 Flash│
│ 200-word brief  │
│ SEBI disclaimer │
└────────┼────────┘
         │
         ▼
┌────────────────────────────────────────────────────┐
│            STREAMLIT UI (6 Tabs)                     │
│ Stock Analysis | Heatmap | Race Chart                │
│ FII/DII | IPO Intelligence | Portfolio Chat          │
└────────────────────────────────────────────────────┘
```

---

## Independent Agents (Tab-level, parallel)

| Agent | Tab | Input | Output |
|---|---|---|---|
| FIIDIIAgent | Tab 4 | NSE public API | Smart money signal + table |
| IPOIntelligenceAgent | Tab 5 | NSE IPO API | AI verdict per IPO |
| PortfolioChatAgent | Tab 6 | Portfolio + query | Source-cited answer |
| MorningBriefingAgent | Header | Nifty + FII/DII | WhatsApp-style brief |

---

## Error Handling & Fallbacks

| Agent | Primary Source | Fallback |
|---|---|---|
| PatternDetectorAgent | yfinance live | 3-day cached data |
| SignalFinderAgent | NSE bulk deal API | yfinance fundamentals only |
| FIIDIIAgent | nseindia.com/api/fiidiiTradeReact | Nifty-derived proxy estimate |
| IPOAgent | NSE IPO API | Static fallback IPO list |
| All Gemini calls | gemini-1.5-flash | Static template response |

---

## Free Data Sources

| Source | Data Type | Endpoint |
|---|---|---|
| Yahoo Finance (yfinance) | OHLCV, fundamentals, news | Python library |
| NSE India FII/DII | Institutional flows | nseindia.com/api/fiidiiTradeReact |
| NSE India Bulk Deals | Large trades | nseindia.com/api/bulk-deals |
| NSE India IPO | Active IPOs | nseindia.com/api/ipo-current-allotment |
| Google Gemini 1.5 Flash | LLM inference | aistudio.google.com |

---

## Deployment

- **Platform:** Streamlit Cloud (share.streamlit.io)
- **Cost:** Free
- **Secrets:** GOOGLE_API_KEY via Streamlit Secrets Manager
- **Repo:** github.com/gopichandchalla16/StockSense-AI
- **Entry point:** ui/streamlit_app.py

---

## Technology Justification

| Tool | Why Chosen | Alternative Considered |
|---|---|---|
| LangGraph | Native multi-agent state machine, visual audit trail | LangChain only (no state) |
| Gemini 1.5 Flash | 1M tokens/day free, fast, multilingual | GPT-4 (paid) |
| yfinance | Free NSE/BSE data, no API key needed | Alpha Vantage (rate limited) |
| pandas-ta | 130+ indicators, pure Python | TA-Lib (complex install) |
| Streamlit | Zero-config deployment, built-in secrets | FastAPI + React (complex) |
| FAISS | Free vector search for future RAG expansion | Pinecone (paid) |

---

*Team NeuralForge | ET GenAI Hackathon 2026*
