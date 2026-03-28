"""
StockSense AI — Main Streamlit Application
Team NeuralForge | ET GenAI Hackathon 2026 | PS #6
6 Tabs: Stock Analysis | Sector Heatmap | Race Chart | FII/DII | IPO | Portfolio Chat
"""
import sys
import os

# ── Critical: add repo root to sys.path
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

from orchestrator.langgraph_flow import analyze_stock
from agents.portfolio_chat import portfolio_chat
from agents.fii_dii_agent import fetch_fii_dii_data, get_smart_money_signal
from agents.ipo_agent import get_ipo_intelligence
from agents.morning_briefing import generate_morning_briefing
from ui.charts.sector_heatmap import build_sector_heatmap
from ui.charts.race_chart import build_race_chart
from utils.ticker_resolver import POPULAR_TICKERS, resolve_ticker

# ── Morning Briefing
if "morning_briefing" not in st.session_state:
    with st.spinner("🌅 Generating today's AI market briefing..."):
        try:
            st.session_state.morning_briefing = generate_morning_briefing()
        except Exception as e:
            st.session_state.morning_briefing = (
                f"🌅 **Morning Briefing unavailable**: {str(e)}\n\n"
                "Check your GOOGLE_API_KEY in Streamlit secrets."
            )

with st.expander("🌅 Today's AI Morning Briefing — tap to expand", expanded=False):
    st.markdown(st.session_state.morning_briefing)

st.markdown("---")

# ── Header
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.title("📈 StockSense AI")
    st.caption("**Team NeuralForge** | ET GenAI Hackathon 2026 | Problem Statement #6")
    st.caption("7-Agent NSE Intelligence: Chart Patterns • Signals • FII/DII • IPOs • Sentiment • Chat")
with col_h2:
    st.markdown("### 🤖 Agent Pipeline")
    st.code(
        "PatternDetector → SignalFinder\n"
        "→ SentimentAnalyzer → ExplainAgent\n"
        "→ PortfolioChat | FII/DII | IPO",
        language=None,
    )

st.markdown("---")

# ── Sidebar
st.sidebar.title("🗂️ My Portfolio")
st.sidebar.caption("Add your NSE holdings for portfolio-aware analysis")
portfolio = []
num = st.sidebar.number_input("Number of holdings", min_value=0, max_value=10, value=2, key="num_stocks")
for i in range(int(num)):
    c1, c2, c3 = st.sidebar.columns(3)
    t = c1.text_input(f"#{i+1} Ticker", key=f"t{i}", placeholder="TCS")
    q = c2.number_input("Qty", key=f"q{i}", min_value=0, value=10)
    p = c3.number_input("₹Avg", key=f"p{i}", min_value=0.0, value=1000.0)
    if t.strip():
        portfolio.append({"ticker": t.strip().upper(), "qty": q, "avg_price": p})
if portfolio:
    st.sidebar.metric("Portfolio Value (Cost)", f"₹{sum(h['qty']*h['avg_price'] for h in portfolio):,.0f}")
st.sidebar.markdown("---")
st.sidebar.caption("🔒 Free stack: yfinance + Gemini + LangGraph")
st.sidebar.caption("🚀 Deployed free on Streamlit Cloud")
st.sidebar.caption("⚠️ Not SEBI-registered investment advice")

# ── Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Stock Analysis", "🌡️ Sector Heatmap", "🏆 Race Chart",
    "🏦 FII/DII Tracker", "🚀 IPO Intelligence", "💬 Portfolio Chat",
])

# ══ TAB 1 ─ STOCK ANALYSIS
with tab1:
    st.subheader("🔍 Multi-Agent Stock Analysis")
    st.caption("4 AI agents: Pattern Detection → Signal Finding → News Sentiment → AI Brief")

    # ── Ticker input + popular quick-select
    c1, c2 = st.columns([4, 1])
    with c1:
        ticker_input = st.text_input(
            "Enter NSE Ticker or Company Name",
            placeholder="e.g. RELIANCE, INFY, TCS, HDFCBANK, SBIN, WIPRO",
            key="main_ticker",
        )
    with c2:
        st.write("")
        st.write("")
        analyze_btn = st.button("🚀 Analyze", type="primary", use_container_width=True)

    # Popular ticker quick buttons
    st.caption("💡 **Quick Select** — click any ticker below:")
    quick_cols = st.columns(10)
    quick_tickers = ["RELIANCE","INFY","TCS","HDFCBANK","ICICIBANK",
                     "SBIN","WIPRO","ITC","MARUTI","TATAMOTORS"]
    for i, qt in enumerate(quick_tickers):
        if quick_cols[i].button(qt, key=f"quick_{qt}"):
            st.session_state["main_ticker"] = qt
            st.rerun()

    # Second row of quick tickers
    quick_cols2 = st.columns(10)
    quick_tickers2 = ["AXISBANK","BAJFINANCE","HCLTECH","TECHM","TITAN",
                      "SUNPHARMA","DRREDDY","LT","BHARTIARTL","ZOMATO"]
    for i, qt in enumerate(quick_tickers2):
        if quick_cols2[i].button(qt, key=f"quick2_{qt}"):
            st.session_state["main_ticker"] = qt
            st.rerun()

    st.markdown("")

    # NSE Ticker reference expander
    with st.expander("📖 NSE Ticker Reference — Company Name → Symbol"):
        st.markdown("""
| Company Name | NSE Ticker | Company Name | NSE Ticker |
|---|---|---|---|
| Infosys | **INFY** | Reliance Industries | **RELIANCE** |
| TCS | **TCS** | HDFC Bank | **HDFCBANK** |
| ICICI Bank | **ICICIBANK** | Axis Bank | **AXISBANK** |
| State Bank (SBI) | **SBIN** | Wipro | **WIPRO** |
| Bajaj Finance | **BAJFINANCE** | HCL Tech | **HCLTECH** |
| Tech Mahindra | **TECHM** | Tata Motors | **TATAMOTORS** |
| Tata Steel | **TATASTEEL** | Maruti Suzuki | **MARUTI** |
| Sun Pharma | **SUNPHARMA** | Dr. Reddy's | **DRREDDY** |
| Cipla | **CIPLA** | Titan | **TITAN** |
| Bharti Airtel | **BHARTIARTL** | L&T | **LT** |
| NTPC | **NTPC** | ONGC | **ONGC** |
| Coal India | **COALINDIA** | ITC | **ITC** |
| Adani Ports | **ADANIPORTS** | Zomato | **ZOMATO** |
| Asian Paints | **ASIANPAINT** | HUL | **HINDUNILVR** |
| IRCTC | **IRCTC** | HAL | **HAL** |
        """)

    if analyze_btn and ticker_input.strip():
        raw_input = ticker_input.strip()
        resolved, was_corrected = resolve_ticker(raw_input)

        if was_corrected:
            st.info(f"🔄 Auto-corrected: **{raw_input.upper()}** → **{resolved}** (NSE symbol)")

        with st.spinner(f"Running 4-agent LangGraph pipeline on **{resolved}**... (15–25s)"):
            result = analyze_stock(raw_input)  # resolve_ticker runs inside analyze_stock

        # Agent Audit Trail
        with st.expander("🤖 Live Agent Activity Log", expanded=True):
            for log in result.get("step_log", []):
                if "✅" in log:    st.success(log)
                elif "❌" in log: st.error(log)
                elif "⚠️" in log: st.warning(log)
                elif "🔄" in log: st.info(log)
                else:              st.info(log)

        pd_data   = result.get("pattern_data") or {}
        sd_data   = result.get("signal_data") or {}
        sent_data = result.get("sentiment_data") or {}
        price     = pd_data.get("current_price", 0)

        if price and price > 0:
            m1,m2,m3,m4,m5 = st.columns(5)
            m1.metric("💰 Price", f"₹{price:,.2f}")
            m2.metric("📅 1D", f"{pd_data['price_change_1d']:+.2f}%", delta=f"{pd_data['price_change_1d']:+.2f}%")
            m3.metric("📆 5D", f"{pd_data['price_change_5d']:+.2f}%", delta=f"{pd_data['price_change_5d']:+.2f}%")
            m4.metric("🏢 Sector", sd_data.get("sector","N/A"))
            sent_score = sent_data.get("sentiment_score", 50)
            m5.metric("📰 Sentiment", sent_data.get("overall_sentiment","NEUTRAL")[:8], f"{sent_score}/100")

            raw = pd_data.get("data", [])
            if raw:
                try:
                    df_c = pd.DataFrame(raw)
                    date_col = "Date" if "Date" in df_c.columns else "index"
                    fig_c = go.Figure(go.Candlestick(
                        x=df_c[date_col], open=df_c["Open"], high=df_c["High"],
                        low=df_c["Low"],  close=df_c["Close"], name=resolved,
                        increasing_line_color="#27ae60", decreasing_line_color="#c0392b"
                    ))
                    fig_c.update_layout(
                        title=f"📈 {resolved} — 90-Day Candlestick (NSE)",
                        template="plotly_dark", height=420,
                        xaxis_rangeslider_visible=False,
                        margin=dict(t=50,l=10,r=10,b=10)
                    )
                    st.plotly_chart(fig_c, use_container_width=True)
                except Exception as e:
                    st.warning(f"Chart render: {e}")

            left, right = st.columns(2)
            with left:
                st.subheader("📈 Chart Patterns")
                for p in pd_data.get("patterns",[]):
                    sig  = p.get("signal","NEUTRAL")
                    icon = "🟢" if "BULL" in sig else "🔴" if "BEAR" in sig else "🟡"
                    st.markdown(f"{icon} **{p['pattern']}**")
                    st.caption(f"{int(p.get('confidence',0.5)*100)}% | {sig}")
                    if p.get("detail"): st.caption(f"↳ {p['detail']}")
                    st.write("")
            with right:
                st.subheader("🎯 Opportunity Signals")
                for s in sd_data.get("signals",[]):
                    icon = "🔥" if s["strength"]=="HIGH" else "⚡" if s["strength"]=="MEDIUM" else "💤"
                    st.markdown(f"{icon} **{s['signal_type']}**")
                    st.caption(s["message"])
                    st.info(f"→ {s['action']}")
                    st.write("")

            fund = sd_data.get("fundamentals",{})
            if any(v for v in fund.values() if v is not None):
                st.subheader("📊 Fundamentals")
                f1,f2,f3,f4 = st.columns(4)
                f1.metric("P/E",      fund.get("pe_ratio","N/A"))
                f2.metric("Div Yield",f"{fund.get('div_yield','N/A')}%")
                f3.metric("52W High", f"₹{fund.get('52w_high','N/A')}")
                f4.metric("52W Low",  f"₹{fund.get('52w_low','N/A')}")

            st.subheader("📰 News Sentiment")
            overall = sent_data.get("overall_sentiment","NEUTRAL")
            s_icon  = "🟢" if "BULL" in overall else "🔴" if "BEAR" in overall else "🟡"
            sc1,sc2 = st.columns([1,2])
            with sc1:
                st.metric(f"{s_icon} Sentiment", overall, f"{sent_score}/100")
            with sc2:
                themes = sent_data.get("key_themes",[])
                if themes: st.markdown("**Themes:** " + " • ".join(themes))
                st.write(sent_data.get("analysis",""))
                if sent_data.get("source_citations"): st.caption(f"📎 {sent_data['source_citations']}")
            with st.expander("📰 Raw Headlines"):
                for n in sent_data.get("raw_news",[]):
                    st.markdown(f"- **{n['title']}** — *{n['publisher']}* ({n['date']})")

            st.markdown("---")
            st.subheader("🧠 AI Market Brief")
            if result.get("explanation"): st.markdown(result["explanation"])

        else:
            # Price is 0 — ticker not found
            ticker_tried = result.get("ticker", raw_input.upper())
            st.error(f"❌ No NSE data found for **'{raw_input.upper()}'** (resolved: {ticker_tried})")
            st.warning("📌 Use the **exact NSE ticker symbol**, not the company name.")
            st.info("""
**Common Mistakes → Correct Tickers:**
- INFOSYS → **INFY** ✅
- HDFC → **HDFCBANK** ✅  
- SBI → **SBIN** ✅
- HCL → **HCLTECH** ✅
- L&T → **LT** ✅
- HUL → **HINDUNILVR** ✅
- BAJAJ FINANCE → **BAJFINANCE** ✅
- TECH MAHINDRA → **TECHM** ✅

Or click any **Quick Select** button above ↑
            """)

    elif not analyze_btn:
        st.info("👆 Enter an NSE ticker or company name above and click Analyze")
        with st.expander("🔍 What does each agent do?"):
            st.markdown("""
1. 🔍 **PatternDetectorAgent** — RSI, MACD, Golden Cross, Bollinger Bands, EMA (pure pandas, no external TA lib)
2. 📡 **SignalFinderAgent** — P/E ratio, 52W proximity, dividend yield, bulk deal signals
3. 📰 **NewsSentimentAgent** — Gemini 2.0 Flash news analysis with source citations
4. 🧠 **ExplanationAgent** — Plain English AI brief with SEBI disclaimer
5. 📊 **Candlestick Chart** — Interactive 90-day Plotly dark-theme chart

All coordinated by **LangGraph StateGraph** with full audit trail.
            """)

# ══ TAB 2 ─ SECTOR HEATMAP
with tab2:
    st.subheader("🌡️ NSE Sector Heatmap — Live")
    st.caption("Size = Market Cap | Color = % change today | 40 stocks × 8 sectors")
    st.warning("⏱️ Takes 20–30 sec — fetching live data for 40 stocks")
    if st.button("🔄 Load Heatmap", type="primary", key="heatmap_btn"):
        with st.spinner("Fetching live sector data..."):
            try:
                st.plotly_chart(build_sector_heatmap(), use_container_width=True)
            except Exception as e:
                st.error(f"Heatmap error: {e}")

# ══ TAB 3 ─ RACE CHART
with tab3:
    st.subheader("🏆 Nifty Top-10 Race Chart")
    st.caption("Animated AI Market Video Engine — performance normalized to base 100")
    st.info("🎥 StockSense AI animated market video — fully data-driven")
    period_sel = st.selectbox("Period", ["6mo","1y","2y"], index=1,
        format_func=lambda x: {"6mo":"6 Months","1y":"1 Year","2y":"2 Years"}[x])
    if st.button("▶ Generate Race Chart", type="primary", key="race_btn"):
        with st.spinner("Building animated race chart..."):
            try:
                fig_race = build_race_chart(period_sel)
                if fig_race.data:
                    st.plotly_chart(fig_race, use_container_width=True)
                    st.caption("▶ Press Play | Base = 100 at start of period")
                else:
                    st.error("No data returned.")
            except Exception as e:
                st.error(f"Race chart: {e}")

# ══ TAB 4 ─ FII/DII
with tab4:
    st.subheader("🏦 FII/DII Smart Money Tracker")
    st.caption("Track institutional capital flows — Foreign & Domestic buying/selling")
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
    with st.expander("📖 How to read FII/DII"):
        st.markdown("""
| Signal | Meaning | Impact |
|---|---|---|
| 🟢 FII Net Buying | Foreign money in | Bullish |
| 🔴 FII Net Selling | Foreign money out | Caution |
| 🟢 DII Net Buying | Domestic absorbing | Support |
| FII Sell + DII Buy | Mixed | Finds support |
        """)

# ══ TAB 5 ─ IPO
with tab5:
    st.subheader("🚀 IPO Intelligence Center")
    st.caption("Gemini 2.0 Flash AI verdict on every active NSE IPO")
    if st.button("🔍 Scan IPO Pipeline", type="primary", key="ipo_btn"):
        with st.spinner("Scanning NSE IPO pipeline..."):
            try:
                ipo_result = get_ipo_intelligence()
                ipos = ipo_result.get("ipos",[])
                st.success(f"Found {ipo_result.get('count',0)} IPO(s)")
                if ipos:
                    for ipo in ipos:
                        with st.expander(f"📋 {ipo.get('company','IPO')} | Opens: {ipo.get('open_date','TBA')}", expanded=True):
                            ic1,ic2,ic3,ic4 = st.columns(4)
                            ic1.metric("Price Band", ipo.get("price_band","TBA"))
                            ic2.metric("GMP", ipo.get("gmp","N/A"))
                            ic3.metric("Issue Size", ipo.get("issue_size","TBA"))
                            ic4.metric("Category", ipo.get("category","Mainboard"))
                            verdict = ipo.get("ai_verdict","Unavailable")
                            st.markdown("**🤖 AI Verdict:**")
                            if "STRONG SUBSCRIBE" in verdict: st.success(verdict)
                            elif "SUBSCRIBE" in verdict:      st.info(verdict)
                            elif "AVOID" in verdict:          st.error(verdict)
                            else:                              st.write(verdict)
                else:
                    st.info("No active IPOs right now.")
            except Exception as e:
                st.error(f"IPO: {e}")

# ══ TAB 6 ─ PORTFOLIO CHAT
with tab6:
    st.subheader("💬 Portfolio-Aware Market Chat")
    st.caption("AI chat — portfolio-aware, source-cited answers")
    if not portfolio:
        st.info("💡 Add holdings in the sidebar for personalized answers")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if not st.session_state.chat_history:
        st.markdown("**💡 Try asking:**")
        suggestions = [
            "Which sector to overweight in 2026?",
            "Should I buy Reliance now?",
            "Build a defensive portfolio",
            "Outlook for IT stocks?",
        ]
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            if cols[i%2].button(s, key=f"sug_{i}"):
                st.session_state.chat_history.append({"role":"user","content":s})
                with st.spinner("Thinking..."):
                    resp = portfolio_chat(s, portfolio, st.session_state.chat_history)
                st.session_state.chat_history.append({"role":"assistant","content":resp})
                st.rerun()
    if prompt := st.chat_input("Ask about your portfolio or any NSE stock..."):
        st.session_state.chat_history.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = portfolio_chat(prompt, portfolio, st.session_state.chat_history)
            st.markdown(response)
        st.session_state.chat_history.append({"role":"assistant","content":response})
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

# ── Footer
st.markdown("---")
st.caption(
    "⚠️ Educational purposes only. Not SEBI-registered advice. | "
    "**Team NeuralForge** | ET GenAI Hackathon 2026 | PS #6"
)
