"""
StockSense AI — Main Streamlit App | NeuralForge | ET GenAI Hackathon 2026 | PS #6
Pro UI with gradient header, live metrics, agent pipeline visualization.
"""
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="StockSense AI | NeuralForge",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── PRO CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Gradient hero header */
.hero-banner {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    border: 1px solid #00d4ff33;
    box-shadow: 0 8px 32px rgba(0,212,255,0.15);
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00d4ff, #7b2ff7, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    letter-spacing: -1px;
}
.hero-subtitle {
    color: #a0c4d8;
    font-size: 1.05rem;
    margin-top: 8px;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(90deg, #7b2ff7, #00d4ff);
    color: white;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 12px;
    margin-right: 8px;
    letter-spacing: 0.5px;
}
/* Agent pipeline steps */
.pipeline-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin: 4px;
}
.pipeline-step {
    color: #00d4ff;
    font-size: 1.6rem;
}
.pipeline-label {
    color: #e0e0e0;
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 4px;
}
.pipeline-arrow {
    color: #7b2ff7;
    font-size: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
}
/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(123,47,247,0.08));
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
/* Status badge */
.status-live {
    display: inline-block;
    width: 8px; height: 8px;
    background: #00ff88;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.5; transform:scale(1.4); }
}
/* Quick ticker buttons */
.stButton > button {
    border-radius: 8px !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    padding: 4px 8px !important;
}
/* Tab styling */
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.88rem;
}
/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1a1a2e; }
::-webkit-scrollbar-thumb { background: #00d4ff44; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

from orchestrator.langgraph_flow import analyze_stock
from agents.portfolio_chat import portfolio_chat
from agents.fii_dii_agent import fetch_fii_dii_data, get_smart_money_signal
from agents.ipo_agent import get_ipo_intelligence
from agents.morning_briefing import generate_morning_briefing
from ui.charts.sector_heatmap import build_sector_heatmap
from ui.charts.race_chart import build_race_chart
from utils.ticker_resolver import resolve_ticker

# ── HERO HEADER
st.markdown("""
<div class="hero-banner">
  <div class="hero-title">📈 StockSense AI</div>
  <div class="hero-subtitle">7-Agent NSE Intelligence Platform — Chart Patterns • Signals • Sentiment • FII/DII • IPOs • Portfolio Chat</div>
  <span class="hero-badge">🏆 ET GenAI Hackathon 2026</span>
  <span class="hero-badge">🧠 Problem Statement #6</span>
  <span class="hero-badge">👥 Team NeuralForge</span>
  <span class="hero-badge"><span class="status-live"></span>LIVE NSE DATA</span>
</div>
""", unsafe_allow_html=True)

# ── AGENT PIPELINE VISUAL
st.markdown("**🤖 Multi-Agent Pipeline:**")
cols = st.columns([2,0.4,2,0.4,2,0.4,2,0.4,2,0.4,2])
steps = [
    ("🔍", "Pattern\nDetector"),
    ("📡", "Signal\nFinder"),
    ("📰", "News\nSentiment"),
    ("🧠", "Explain\nAgent"),
    ("💬", "Portfolio\nChat"),
    ("🏦", "FII/DII\n+ IPO"),
]
for idx, (icon, label) in enumerate(steps):
    with cols[idx*2]:
        st.markdown(f"""
        <div class="pipeline-card">
          <div class="pipeline-step">{icon}</div>
          <div class="pipeline-label">{label.replace(chr(10),"<br>")}</div>
        </div>""", unsafe_allow_html=True)
    if idx < len(steps)-1:
        with cols[idx*2+1]:
            st.markdown('<div class="pipeline-arrow">→</div>', unsafe_allow_html=True)

st.markdown("")

# ── Morning Briefing
if "morning_briefing" not in st.session_state:
    with st.spinner("🌅 Generating AI morning briefing..."):
        try:
            st.session_state.morning_briefing = generate_morning_briefing()
        except Exception as e:
            st.session_state.morning_briefing = f"🌅 Briefing unavailable: {e}"

with st.expander("🌅 Today's AI Morning Briefing — click to expand", expanded=False):
    st.markdown(st.session_state.morning_briefing)

st.markdown("---")

# ── Sidebar
st.sidebar.markdown("""
<div style='background:linear-gradient(135deg,#0f2027,#2c5364);padding:16px;border-radius:12px;margin-bottom:16px;border:1px solid #00d4ff33'>
<h3 style='color:#00d4ff;margin:0'>🗂️ My Portfolio</h3>
<p style='color:#a0c4d8;font-size:0.8rem;margin:4px 0 0'>NSE holdings for AI-powered analysis</p>
</div>""", unsafe_allow_html=True)
portfolio = []
num = st.sidebar.number_input("Holdings", min_value=0, max_value=10, value=0, key="num_stocks")
for i in range(int(num)):
    c1, c2, c3 = st.sidebar.columns(3)
    t = c1.text_input(f"#{i+1}", key=f"t{i}", placeholder="TCS")
    q = c2.number_input("Qty", key=f"q{i}", min_value=0, value=10)
    p = c3.number_input("₹", key=f"p{i}", min_value=0.0, value=1000.0)
    if t.strip():
        portfolio.append({"ticker": t.strip().upper(), "qty": q, "avg_price": p})
if portfolio:
    total_v = sum(h["qty"]*h["avg_price"] for h in portfolio)
    st.sidebar.metric("💼 Portfolio Value", f"₹{total_v:,.0f}")
st.sidebar.markdown("---")
st.sidebar.info("🔒 Stack: yfinance + Gemini 2.0 + HuggingFace + LangGraph\n\n🚀 Free deployment on Streamlit Cloud")
st.sidebar.warning("⚠️ Not SEBI-registered investment advice")

# ── TABS
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Stock Analysis", "🌡️ Sector Heatmap", "🏆 Race Chart",
    "🏦 FII/DII Tracker", "🚀 IPO Intelligence", "💬 Portfolio Chat",
])

# ══════ TAB 1 ─ STOCK ANALYSIS ════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🔍 Multi-Agent Stock Analysis")
    st.caption("Supports **any NSE-listed stock** — enter ticker symbol or company name")

    # Quick select using session state callbacks (no crash)
    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = ""

    def set_ticker(t):
        st.session_state.selected_ticker = t

    st.caption("📌 **Quick Select** — Nifty 50 Top Stocks:")
    row1 = ["RELIANCE","INFY","TCS","HDFCBANK","ICICIBANK","SBIN","WIPRO","ITC","MARUTI","TATAMOTORS"]
    row2 = ["AXISBANK","BAJFINANCE","HCLTECH","TECHM","TITAN","SUNPHARMA","DRREDDY","LT","BHARTIARTL","ZOMATO"]
    row3 = ["ADANIPORTS","NTPC","POWERGRID","ONGC","COALINDIA","HINDUNILVR","ASIANPAINT","ULTRACEMCO","GRASIM","NESTLEIND"]

    c_row1 = st.columns(10)
    for i, qt in enumerate(row1):
        if c_row1[i].button(qt, key=f"r1_{qt}", on_click=set_ticker, args=(qt,)):
            pass
    c_row2 = st.columns(10)
    for i, qt in enumerate(row2):
        if c_row2[i].button(qt, key=f"r2_{qt}", on_click=set_ticker, args=(qt,)):
            pass
    c_row3 = st.columns(10)
    for i, qt in enumerate(row3):
        if c_row3[i].button(qt, key=f"r3_{qt}", on_click=set_ticker, args=(qt,)):
            pass

    st.markdown("")

    # Input box — pre-filled from quick select
    default_val = st.session_state.selected_ticker
    c1, c2 = st.columns([5, 1])
    with c1:
        ticker_input = st.text_input(
            "🔎 Enter any NSE Ticker or Company Name",
            value=default_val,
            placeholder="Any NSE stock: RELIANCE, INFY, BAJAJFINSV, NESTLEIND, PIDILITIND...",
            key="main_ticker_input",
        )
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🚀 Analyze", type="primary", use_container_width=True)

    # NSE Reference
    with st.expander("📖 NSE Ticker Reference — any company → symbol"):
        st.markdown("""
| Company | NSE Ticker | Company | NSE Ticker | Company | NSE Ticker |
|---|---|---|---|---|---|
| Infosys | **INFY** | Reliance | **RELIANCE** | HDFC Bank | **HDFCBANK** |
| TCS | **TCS** | ICICI Bank | **ICICIBANK** | Axis Bank | **AXISBANK** |
| SBI | **SBIN** | Wipro | **WIPRO** | Bajaj Finance | **BAJFINANCE** |
| HCL Tech | **HCLTECH** | Tech Mahindra | **TECHM** | Tata Motors | **TATAMOTORS** |
| Tata Steel | **TATASTEEL** | Maruti Suzuki | **MARUTI** | Sun Pharma | **SUNPHARMA** |
| Dr. Reddy's | **DRREDDY** | Cipla | **CIPLA** | Titan | **TITAN** |
| Airtel | **BHARTIARTL** | L&T | **LT** | NTPC | **NTPC** |
| ONGC | **ONGC** | Coal India | **COALINDIA** | ITC | **ITC** |
| Adani Ports | **ADANIPORTS** | Zomato | **ZOMATO** | Asian Paints | **ASIANPAINT** |
| HUL | **HINDUNILVR** | IRCTC | **IRCTC** | HAL | **HAL** |
| Bajaj Finserv | **BAJAJFINSV** | Nestle India | **NESTLEIND** | Pidilite | **PIDILITIND** |
| JSW Steel | **JSWSTEEL** | Tata Power | **TATAPOWER** | Havells | **HAVELLS** |
| Berger Paints | **BERGEPAINT** | Siemens | **SIEMENS** | Divi's Labs | **DIVISLAB** |
| Apollo Hospital | **APOLLOHOSP** | Nykaa | **FSN** | Paytm | **PAYTM** |
        """)

    if analyze_btn and ticker_input.strip():
        raw_input   = ticker_input.strip()
        resolved, _ = resolve_ticker(raw_input)

        st.markdown(f"""
        <div style='background:linear-gradient(90deg,rgba(0,212,255,0.1),rgba(123,47,247,0.1));
        border:1px solid #00d4ff44;border-radius:10px;padding:12px 20px;margin-bottom:16px'>
        🚀 Running <b>4-Agent LangGraph Pipeline</b> on <b style='color:#00d4ff'>{resolved}</b> — Please wait 15–25 seconds...
        </div>""", unsafe_allow_html=True)

        with st.spinner(f"Analyzing {resolved}..."):
            result = analyze_stock(raw_input)

        with st.expander("🤖 Live Agent Audit Trail", expanded=True):
            for log in result.get("step_log", []):
                if "✅" in log:    st.success(log)
                elif "❌" in log: st.error(log)
                elif "⚠️" in log: st.warning(log)
                elif "🔄" in log: st.info(log)
                else:              st.info(log)

        pd_data   = result.get("pattern_data") or {}
        sd_data   = result.get("signal_data")   or {}
        sent_data = result.get("sentiment_data") or {}
        price     = pd_data.get("current_price", 0)

        if price and price > 0:
            # ── Metric Cards
            st.markdown("")
            m1,m2,m3,m4,m5 = st.columns(5)
            change_1d  = pd_data.get("price_change_1d", 0)
            change_5d  = pd_data.get("price_change_5d", 0)
            sent_score = sent_data.get("sentiment_score", 50)
            overall_s  = sent_data.get("overall_sentiment", "NEUTRAL")

            m1.metric("💰 Current Price",  f"₹{price:,.2f}")
            m2.metric("📅 1-Day Change",  f"{change_1d:+.2f}%",  delta=f"{change_1d:+.2f}%")
            m3.metric("📆 5-Day Change",  f"{change_5d:+.2f}%",  delta=f"{change_5d:+.2f}%")
            m4.metric("🏢 Sector",        sd_data.get("sector","N/A"))
            m5.metric("📰 News Sentiment", f"{overall_s[:8]}",     f"{sent_score}/100")

            # ── Candlestick chart
            raw = pd_data.get("data", [])
            if raw:
                try:
                    df_c     = pd.DataFrame(raw)
                    date_col = "Date" if "Date" in df_c.columns else "index"
                    fig_c    = go.Figure(go.Candlestick(
                        x=df_c[date_col],
                        open=df_c["Open"], high=df_c["High"],
                        low=df_c["Low"],   close=df_c["Close"],
                        name=resolved,
                        increasing_line_color="#00ff88",
                        decreasing_line_color="#ff4444",
                    ))
                    fig_c.update_layout(
                        title=dict(text=f"📈 {resolved} — 90-Day Candlestick Chart (NSE)",
                                   font=dict(color="#00d4ff", size=16)),
                        template="plotly_dark",
                        height=440,
                        xaxis_rangeslider_visible=False,
                        paper_bgcolor="rgba(15,32,39,0.8)",
                        plot_bgcolor="rgba(15,32,39,0.8)",
                        margin=dict(t=55, l=10, r=10, b=10),
                        xaxis=dict(gridcolor="#ffffff11"),
                        yaxis=dict(gridcolor="#ffffff11"),
                    )
                    st.plotly_chart(fig_c, use_container_width=True)
                except Exception as e:
                    st.warning(f"Chart: {e}")

            # ── Patterns + Signals
            left, right = st.columns(2)
            with left:
                st.markdown("#### 📈 Detected Chart Patterns")
                for p in pd_data.get("patterns", []):
                    sig  = p.get("signal", "NEUTRAL")
                    icon = "🟢" if "BULL" in sig else "🔴" if "BEAR" in sig else "🟡"
                    conf = int(p.get("confidence", 0.5) * 100)
                    st.markdown(
                        f"<div style='background:rgba(255,255,255,0.04);border-left:3px solid "
                        f"{'#00ff88' if 'BULL' in sig else '#ff4444' if 'BEAR' in sig else '#ffcc00'};"
                        f"padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0'>"
                        f"{icon} <b>{p['pattern']}</b><br>"
                        f"<small style='color:#a0c4d8'>{conf}% confidence | {sig}</small>"
                        f"{'<br><small style=color:#718096>' + p.get('detail','') + '</small>' if p.get('detail') else ''}"
                        f"</div>",
                        unsafe_allow_html=True
                    )

            with right:
                st.markdown("#### 🎯 Opportunity Signals")
                for s in sd_data.get("signals", []):
                    strength = s.get("strength", "LOW")
                    color    = "#00ff88" if strength=="HIGH" else "#ffcc00" if strength=="MEDIUM" else "#a0c4d8"
                    icon     = "🔥" if strength=="HIGH" else "⚡" if strength=="MEDIUM" else "💤"
                    st.markdown(
                        f"<div style='background:rgba(255,255,255,0.04);border-left:3px solid {color};"
                        f"padding:10px 14px;border-radius:0 8px 8px 0;margin:6px 0'>"
                        f"{icon} <b>{s['signal_type']}</b><br>"
                        f"<small style='color:#a0c4d8'>{s['message']}</small><br>"
                        f"<small style='color:{color}'>→ {s['action']}</small>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

            # ── Fundamentals
            fund = sd_data.get("fundamentals", {})
            if any(v for v in fund.values() if v is not None):
                st.markdown("#### 📊 Key Fundamentals")
                f1,f2,f3,f4 = st.columns(4)
                f1.metric("P/E Ratio",  fund.get("pe_ratio","N/A"))
                f2.metric("Div Yield",  f"{fund.get('div_yield','N/A')}%")
                f3.metric("52W High",   f"₹{fund.get('52w_high','N/A')}")
                f4.metric("52W Low",    f"₹{fund.get('52w_low','N/A')}")

            # ── News Sentiment
            st.markdown("#### 📰 News Sentiment Analysis")
            s_icon = "🟢" if "BULL" in overall_s else "🔴" if "BEAR" in overall_s else "🟡"
            sc1, sc2 = st.columns([1,2])
            with sc1:
                st.metric(f"{s_icon} Sentiment", overall_s, f"{sent_score}/100")
            with sc2:
                themes = sent_data.get("key_themes",[])
                if themes: st.markdown("**Themes:** " + " • ".join(themes))
                st.write(sent_data.get("analysis",""))
            with st.expander("📰 Raw News Headlines"):
                for n in sent_data.get("raw_news",[]):
                    st.markdown(f"- [{n['title']}]({n.get('url','#')}) — *{n['publisher']}* ({n['date']})", unsafe_allow_html=False)

            # ── AI Brief
            st.markdown("---")
            st.markdown("#### 🧠 AI Market Brief")
            expl = result.get("explanation","")
            if expl:
                st.markdown(
                    f"<div style='background:linear-gradient(135deg,rgba(0,212,255,0.06),rgba(123,47,247,0.06));"
                    f"border:1px solid rgba(0,212,255,0.2);border-radius:12px;padding:20px'>{expl}</div>",
                    unsafe_allow_html=True
                )

        else:
            # ── Smart error: ticker not found
            st.markdown(f"""
            <div style='background:rgba(255,68,68,0.1);border:1px solid #ff444466;
            border-radius:12px;padding:20px;'>
            ❌ <b>No NSE data found for '{raw_input.upper()}'</b><br><br>
            📌 <b>Make sure you're using the exact NSE ticker symbol:</b><br>
            &nbsp;&nbsp;• INFOSYS → <b>INFY</b> &nbsp;&nbsp;• HDFC → <b>HDFCBANK</b> &nbsp;&nbsp;• SBI → <b>SBIN</b><br>
            &nbsp;&nbsp;• HCL → <b>HCLTECH</b> &nbsp;&nbsp;• L&T → <b>LT</b> &nbsp;&nbsp;• HUL → <b>HINDUNILVR</b><br><br>
            📖 Check the <b>NSE Ticker Reference</b> table above ↑
            </div>""", unsafe_allow_html=True)

    elif not analyze_btn:
        st.markdown("""
        <div style='background:rgba(0,212,255,0.06);border:1px dashed #00d4ff44;
        border-radius:12px;padding:24px;text-align:center;'>
        <div style='font-size:2rem'>👆</div>
        <div style='color:#a0c4d8;margin-top:8px'>Click a <b>Quick Select</b> button above or type any NSE ticker, then click <b>🚀 Analyze</b></div>
        <div style='color:#718096;font-size:0.85rem;margin-top:8px'>Supports all NSE-listed stocks — Nifty 50, Nifty 200, SME, and more</div>
        </div>""", unsafe_allow_html=True)
        with st.expander("🔍 What does each agent do?"):
            st.markdown("""
1. 🔍 **PatternDetectorAgent** — RSI-14, MACD(12,26,9), Golden/Death Cross, Bollinger Bands, EMA 20/50 (pure pandas)
2. 📡 **SignalFinderAgent** — P/E ratio, 52W proximity, dividend yield, bulk deals
3. 📰 **NewsSentimentAgent** — Gemini 2.0 Flash / HuggingFace Mistral-7B news analysis
4. 🧠 **ExplanationAgent** — Plain English AI brief (Gemini → HF fallback → rule-based)
5. 📊 **Candlestick Chart** — 90-day interactive Plotly dark-theme chart

**LangGraph StateGraph** coordinates all agents with a full audit trail.
            """)

# ══════ TAB 2 ─ SECTOR HEATMAP
with tab2:
    st.markdown("### 🌡️ NSE Sector Heatmap — Live Performance")
    st.caption("Size = Market Cap weight | Color = % change today | 40 stocks × 8 sectors")
    st.warning("⏱️ Loading takes 20–30 seconds — fetching live data for 40 NSE stocks")
    if st.button("🔄 Load Live Heatmap", type="primary", key="heatmap_btn"):
        with st.spinner("Fetching live data for 8 sectors..."):
            try:
                fig_heat = build_sector_heatmap()
                st.plotly_chart(fig_heat, use_container_width=True)
                st.caption("🟢 Green = gaining | 🔴 Red = losing | Size = market cap weight")
            except Exception as e:
                st.error(f"Heatmap error: {e}")

# ══════ TAB 3 ─ RACE CHART
with tab3:
    st.markdown("### 🏆 Nifty Top-10 Performance Race Chart")
    st.caption("AI Market Video Engine — animated, data-driven visual market update | Base = 100")
    st.info("🎥 StockSense AI's answer to the AI Market Video Engine sub-problem — no static slides, fully animated")
    period_sel = st.selectbox("Time Period", ["6mo","1y","2y"], index=1,
        format_func=lambda x: {"6mo":"6 Months","1y":"1 Year","2y":"2 Years"}[x])
    if st.button("▶ Generate Race Chart", type="primary", key="race_btn"):
        with st.spinner("Building animated race chart from NSE historical data..."):
            try:
                fig_race = build_race_chart(period_sel)
                if fig_race.data:
                    st.plotly_chart(fig_race, use_container_width=True)
                    st.caption("▶ Press Play on the chart to animate | Base = 100 at period start")
                else:
                    st.error("No data returned. Try again.")
            except Exception as e:
                st.error(f"Race chart error: {e}")

# ══════ TAB 4 ─ FII/DII
with tab4:
    st.markdown("### 🏦 Smart Money Flow — FII/DII Institutional Tracker")
    st.caption("Track where Foreign & Domestic institutions are deploying or withdrawing capital")
    if st.button("📡 Fetch FII/DII Data", type="primary", key="fiidii_btn"):
        with st.spinner("Connecting to NSE FII/DII feed..."):
            try:
                fii_data = fetch_fii_dii_data()
                signal   = get_smart_money_signal(fii_data)
                icon = "🟢" if "BUYING" in signal else "🔴" if "SELLING" in signal else "🟡"
                st.markdown(f"## {icon} {signal}")
                st.caption(f"Source: **{fii_data.get('source','NSE India')}**")
                records = fii_data.get("data",[])
                if records:
                    st.dataframe(pd.DataFrame(records[:12]), use_container_width=True, height=380)
            except Exception as e:
                st.error(f"FII/DII: {e}")
    with st.expander("📖 How to read FII/DII data"):
        st.markdown("""
| Signal | Meaning | Market Impact |
|---|---|---|
| 🟢 FII Net Buying | Foreign money entering India | Bullish |
| 🔴 FII Net Selling | Foreign money exiting India | Caution |
| 🟢 DII Net Buying | Domestic institutions absorbing | Support |
| FII Sell + DII Buy | Mixed flows | Market finds support at lows |
| Both Buying | Strong conviction | Strong bullish signal |
        """)

# ══════ TAB 5 ─ IPO
with tab5:
    st.markdown("### 🚀 IPO Intelligence Center")
    st.caption("AI-powered IPO analysis — Gemini 2.0 Flash verdict on every active/upcoming NSE IPO")
    if st.button("🔍 Scan IPO Pipeline", type="primary", key="ipo_btn"):
        with st.spinner("Scanning NSE IPO pipeline + generating AI verdicts..."):
            try:
                ipo_result = get_ipo_intelligence()
                ipos = ipo_result.get("ipos",[])
                st.success(f"Found {ipo_result.get('count',0)} IPO(s) in pipeline")
                if ipos:
                    for ipo in ipos:
                        with st.expander(f"📋 {ipo.get('company','IPO')} | Opens: {ipo.get('open_date','TBA')}", expanded=True):
                            ic1,ic2,ic3,ic4 = st.columns(4)
                            ic1.metric("Price Band", ipo.get("price_band","TBA"))
                            ic2.metric("GMP",        ipo.get("gmp","N/A"))
                            ic3.metric("Issue Size", ipo.get("issue_size","TBA"))
                            ic4.metric("Category",   ipo.get("category","Mainboard"))
                            verdict = ipo.get("ai_verdict","Unavailable")
                            st.markdown("**🤖 AI Verdict:**")
                            if "STRONG SUBSCRIBE" in verdict: st.success(verdict)
                            elif "SUBSCRIBE" in verdict:      st.info(verdict)
                            elif "AVOID" in verdict:          st.error(verdict)
                            else:                              st.write(verdict)
                else:
                    st.info("No active IPOs right now. Check back during IPO window.")
            except Exception as e:
                st.error(f"IPO error: {e}")

# ══════ TAB 6 ─ PORTFOLIO CHAT
with tab6:
    st.markdown("### 💬 Portfolio-Aware Market Chat")
    st.caption("AI market assistant — portfolio-aware, source-cited, multi-step reasoning")
    if not portfolio:
        st.info("💡 Add your NSE holdings in the sidebar for personalized portfolio analysis")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if not st.session_state.chat_history:
        st.markdown("**💡 Try asking:**")
        suggestions = [
            "Which sector to overweight in 2026?",
            "Should I buy Reliance at current levels?",
            "Build a defensive portfolio for correction",
            "Outlook for IT stocks this quarter?",
        ]
        scols = st.columns(2)
        for i, s in enumerate(suggestions):
            if scols[i%2].button(s, key=f"sug_{i}"):
                st.session_state.chat_history.append({"role":"user","content":s})
                with st.spinner("Thinking..."):
                    resp = portfolio_chat(s, portfolio, st.session_state.chat_history)
                st.session_state.chat_history.append({"role":"assistant","content":resp})
                st.rerun()
    if prompt := st.chat_input("Ask about your portfolio or any NSE stock..."):
        st.session_state.chat_history.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing portfolio and market data..."):
                response = portfolio_chat(prompt, portfolio, st.session_state.chat_history)
            st.markdown(response)
        st.session_state.chat_history.append({"role":"assistant","content":response})
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

# ── Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#718096;font-size:0.82rem;padding:12px'>
⚠️ StockSense AI is for educational purposes only. Not SEBI-registered investment advice.<br>
Always conduct your own research and consult a SEBI-registered advisor before investing.<br>
<b style='color:#a0c4d8'>Team NeuralForge</b> | ET GenAI Hackathon 2026 | Problem Statement #6
</div>""", unsafe_allow_html=True)
