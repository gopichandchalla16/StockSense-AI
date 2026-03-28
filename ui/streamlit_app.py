"""
StockSense AI — Main Streamlit App
NeuralForge | ET GenAI Hackathon 2026 | Problem Statement #6
Fully fixed: no raw errors, valid hex colors, clean judge-ready UI
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
    page_icon="\U0001f4c8",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #070d1a; }
.hero-wrap {
    background: linear-gradient(135deg, #0a1628 0%, #112040 50%, #0a1628 100%);
    border: 1px solid #00d4ff30;
    border-radius: 20px;
    padding: 36px 44px 28px;
    margin-bottom: 6px;
    box-shadow: 0 0 60px rgba(0,212,255,0.08);
}
.hero-logo { font-size: 2.8rem; font-weight: 900; letter-spacing: -1px;
    background: linear-gradient(90deg, #00d4ff, #7b2ff7 50%, #00d4ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub  { color: #7a9bb5; font-size: 1rem; margin: 6px 0 16px; }
.badge { display:inline-block; padding:4px 13px; border-radius:20px; font-size:.76rem; font-weight:700; margin-right:8px; letter-spacing:.4px; }
.badge-blue   { background:rgba(0,212,255,0.12); color:#00d4ff; border:1px solid #00d4ff40; }
.badge-purple { background:rgba(123,47,247,0.12); color:#a07cf7; border:1px solid #7b2ff740; }
.badge-green  { background:rgba(0,255,136,0.12); color:#00ff88; border:1px solid #00ff8840; }
.badge-live   { background:rgba(0,255,136,0.15); color:#00ff88; border:1px solid #00ff8855; }
.dot { display:inline-block; width:7px; height:7px; background:#00ff88; border-radius:50%; margin-right:5px; animation:pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.5)} }
.pipeline-wrap { display:flex; align-items:center; gap:6px; margin:10px 0 4px; overflow-x:auto; padding:4px 0; }
.pipe-step { background:rgba(255,255,255,.03); border:1px solid rgba(0,212,255,.2); border-radius:10px; padding:10px 14px; text-align:center; min-width:80px; flex-shrink:0; }
.pipe-icon { font-size:1.3rem; }
.pipe-lbl  { font-size:.68rem; color:#a0c4d8; font-weight:600; margin-top:3px; line-height:1.3; }
.pipe-arr  { color:#7b2ff7; font-size:1.3rem; flex-shrink:0; }
.pattern-pill { border-left:3px solid; border-radius:0 10px 10px 0; padding:10px 14px; margin:6px 0; background:rgba(255,255,255,.03); }
.sig-pill     { border-left:3px solid; border-radius:0 10px 10px 0; padding:10px 14px; margin:6px 0; background:rgba(255,255,255,.03); }
.ai-card { background:linear-gradient(135deg,rgba(0,212,255,.05),rgba(123,47,247,.05)); border:1px solid rgba(0,212,255,.18); border-radius:14px; padding:20px; }
.result-title { color:#00d4ff; font-size:1rem; font-weight:700; margin:12px 0 8px; }
.stTabs [data-baseweb="tab"] { font-weight:700; font-size:.88rem; }
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0a1628; }
::-webkit-scrollbar-thumb { background:rgba(0,212,255,0.2); border-radius:3px; }
</style>
""", unsafe_allow_html=True)

from orchestrator.langgraph_flow import analyze_stock
from agents.portfolio_chat    import portfolio_chat
from agents.fii_dii_agent     import fetch_fii_dii_data, get_smart_money_signal
from agents.ipo_agent         import get_ipo_intelligence
from agents.morning_briefing  import generate_morning_briefing
from ui.charts.sector_heatmap import build_sector_heatmap, build_sector_bar_chart, build_top_movers_chart
from ui.charts.race_chart     import build_race_chart
from utils.ticker_resolver    import resolve_ticker

# ══ HERO
st.markdown("""
<div class="hero-wrap">
  <div class="hero-logo">📈 StockSense AI</div>
  <div class="hero-sub">7-Agent NSE Intelligence Platform — Chart Patterns • Signals • Sentiment • FII/DII • IPOs • Portfolio Chat</div>
  <span class="badge badge-blue">🏆 ET GenAI Hackathon 2026</span>
  <span class="badge badge-purple">🧠 Problem Statement #6</span>
  <span class="badge badge-green">👥 Team NeuralForge</span>
  <span class="badge badge-live"><span class="dot"></span>LIVE NSE DATA</span>
</div>
""", unsafe_allow_html=True)

# ══ Pipeline visual
st.markdown("<p style='color:#5a7a96;font-size:.8rem;font-weight:700;letter-spacing:1px;margin:12px 0 4px'>🤖 MULTI-AGENT PIPELINE</p>", unsafe_allow_html=True)
st.markdown("""
<div class="pipeline-wrap">
  <div class="pipe-step"><div class="pipe-icon">🔍</div><div class="pipe-lbl">Pattern<br>Detector</div></div>
  <div class="pipe-arr">→</div>
  <div class="pipe-step"><div class="pipe-icon">📡</div><div class="pipe-lbl">Signal<br>Finder</div></div>
  <div class="pipe-arr">→</div>
  <div class="pipe-step"><div class="pipe-icon">📰</div><div class="pipe-lbl">News<br>Sentiment</div></div>
  <div class="pipe-arr">→</div>
  <div class="pipe-step"><div class="pipe-icon">🧠</div><div class="pipe-lbl">AI<br>Explain</div></div>
  <div class="pipe-arr">→</div>
  <div class="pipe-step"><div class="pipe-icon">💬</div><div class="pipe-lbl">Portfolio<br>Chat</div></div>
  <div class="pipe-arr">→</div>
  <div class="pipe-step"><div class="pipe-icon">🏦</div><div class="pipe-lbl">FII/DII<br>+ IPO</div></div>
</div>
""", unsafe_allow_html=True)

# ══ Morning Briefing
if "morning_briefing" not in st.session_state:
    try:
        st.session_state.morning_briefing = generate_morning_briefing()
    except Exception:
        st.session_state.morning_briefing = "🌅 Market brief loading... Please refresh."

with st.expander("🌅 Today's AI Morning Briefing — click to expand", expanded=False):
    st.markdown(st.session_state.morning_briefing)

st.markdown("---")

# ══ SIDEBAR
st.sidebar.markdown("""
<div style='background:linear-gradient(135deg,#0a1628,#112040);padding:16px;
border-radius:12px;margin-bottom:14px;border:1px solid rgba(0,212,255,0.15)'>
<h3 style='color:#00d4ff;margin:0 0 4px'>🗂️ My Portfolio</h3>
<p style='color:#5a7a96;font-size:.8rem;margin:0'>Add NSE holdings for AI-powered analysis</p></div>
""", unsafe_allow_html=True)
portfolio = []
num = st.sidebar.number_input("Number of holdings", min_value=0, max_value=10, value=0, key="num_stocks")
for i in range(int(num)):
    c1, c2, c3 = st.sidebar.columns(3)
    t = c1.text_input(f"#{i+1} Ticker", key=f"t{i}", placeholder="TCS")
    q = c2.number_input("Qty",   key=f"q{i}", min_value=0, value=10)
    p = c3.number_input("₹Avg",  key=f"p{i}", min_value=0.0, value=1000.0, format="%.2f")
    if t.strip():
        portfolio.append({"ticker": t.strip().upper(), "qty": q, "avg_price": p})
if portfolio:
    total_v = sum(h["qty"] * h["avg_price"] for h in portfolio)
    st.sidebar.metric("💼 Total Value", f"₹{total_v:,.0f}")
st.sidebar.markdown("---")
st.sidebar.caption("🔒 Stack: yfinance · Gemini 2.0 · HuggingFace Mistral · LangGraph")
st.sidebar.warning("⚠️ Not SEBI-registered investment advice")

# ══ TABS
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Stock Analysis",
    "🌡️ Sector Heatmap",
    "🏆 Race Chart",
    "🏦 FII/DII Tracker",
    "🚀 IPO Intelligence",
    "💬 Portfolio Chat",
])

# ════════ TAB 1 — STOCK ANALYSIS
with tab1:
    st.markdown("")
    st.markdown("""
    <div style='background:linear-gradient(90deg,rgba(0,212,255,.08),transparent);
    border-left:3px solid #00d4ff;border-radius:0 8px 8px 0;padding:12px 18px;margin-bottom:10px'>
    <span style='color:#00d4ff;font-weight:800;font-size:1.05rem'>🔍 Multi-Agent Stock Analysis</span><br>
    <span style='color:#5a7a96;font-size:.85rem'>4 AI agents analyze any NSE stock —
    Pattern Detection → Signal Finding → News Sentiment → AI Brief</span>
    </div>
    """, unsafe_allow_html=True)

    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = ""
    if "search_stock" not in st.session_state:
        st.session_state.search_stock = ""

    def _set(t):
        st.session_state.selected_ticker = t
        st.session_state.search_stock    = t

    st.markdown("<p style='color:#5a7a96;font-size:.8rem;font-weight:700;margin:8px 0 6px'>⚡ QUICK DEMO STOCKS</p>", unsafe_allow_html=True)
    cc1, cc2, cc3, cc4, cc5 = st.columns(5)
    with cc1:
        if st.button("Reliance",   use_container_width=True, on_click=_set, args=("RELIANCE",)):  pass
    with cc2:
        if st.button("Infosys",    use_container_width=True, on_click=_set, args=("INFY",)):      pass
    with cc3:
        if st.button("HDFC Bank",  use_container_width=True, on_click=_set, args=("HDFCBANK",)): pass
    with cc4:
        if st.button("TCS",        use_container_width=True, on_click=_set, args=("TCS",)):       pass
    with cc5:
        if st.button("Tata Motors",use_container_width=True, on_click=_set, args=("TATAMOTORS",)):pass

    st.markdown("")
    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        ticker_input = st.text_input(
            "🔎 Search any NSE stock (ticker or company name)",
            value=st.session_state.get("search_stock", ""),
            placeholder="Type: RELIANCE, INFY, HDFCBANK, TATAMOTORS, SUNPHARMA, PAYTM, IRCTC...",
            key="main_ticker_input",
        )
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        analyze_btn = st.button("🚀 Analyze", type="primary", use_container_width=True)

    with st.expander("📖 NSE Ticker Reference — find any company symbol", expanded=False):
        st.markdown("""
| Company | Ticker | Company | Ticker | Company | Ticker |
|---|---|---|---|---|---|
| Reliance | **RELIANCE** | Infosys | **INFY** | HDFC Bank | **HDFCBANK** |
| TCS | **TCS** | ICICI Bank | **ICICIBANK** | Axis Bank | **AXISBANK** |
| SBI | **SBIN** | Wipro | **WIPRO** | Bajaj Finance | **BAJFINANCE** |
| HCL Tech | **HCLTECH** | Tech Mahindra | **TECHM** | Tata Motors | **TATAMOTORS** |
| Tata Steel | **TATASTEEL** | Maruti | **MARUTI** | Sun Pharma | **SUNPHARMA** |
| Dr Reddy | **DRREDDY** | Cipla | **CIPLA** | Titan | **TITAN** |
| Airtel | **BHARTIARTL** | L&T | **LT** | NTPC | **NTPC** |
| ONGC | **ONGC** | Coal India | **COALINDIA** | ITC | **ITC** |
| Adani Ports | **ADANIPORTS** | Zomato | **ZOMATO** | Asian Paints | **ASIANPAINT** |
| HUL | **HINDUNILVR** | IRCTC | **IRCTC** | HAL | **HAL** |
| Bajaj Finserv | **BAJAJFINSV** | Nestle | **NESTLEIND** | Pidilite | **PIDILITIND** |
| JSW Steel | **JSWSTEEL** | Tata Power | **TATAPOWER** | Paytm | **PAYTM** |
| Apollo Hosp | **APOLLOHOSP** | Divi's Labs | **DIVISLAB** | Nykaa | **FSN** |
        """)

    if analyze_btn and ticker_input.strip():
        raw_input   = ticker_input.strip()
        resolved, _ = resolve_ticker(raw_input)
        if resolved.upper() != raw_input.upper():
            st.info(f"✅ Auto-resolved **{raw_input.upper()}** → **{resolved}**")
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,rgba(0,212,255,.08),rgba(123,47,247,.08));
        border:1px solid rgba(0,212,255,0.2);border-radius:10px;padding:12px 20px;margin:10px 0'>
        🚀 Running <b>4-Agent LangGraph Pipeline</b> on
        <b style='color:#00d4ff'>{resolved}.NS</b>…
        </div>""", unsafe_allow_html=True)
        with st.spinner(f"Analyzing {resolved}… (15-25 sec)"):
            result = analyze_stock(raw_input)
        pd_data   = result.get("pattern_data")  or {}
        sd_data   = result.get("signal_data")    or {}
        sent_data = result.get("sentiment_data") or {}
        price     = pd_data.get("current_price", 0)

        if price and price > 0:
            change_1d  = pd_data.get("price_change_1d", 0)
            change_5d  = pd_data.get("price_change_5d", 0)
            sent_score = sent_data.get("sentiment_score", 50)
            overall_s  = sent_data.get("overall_sentiment", "NEUTRAL")
            s_emoji    = "🟢" if "BULL" in overall_s else "🔴" if "BEAR" in overall_s else "🟡"
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("💰 Price",    f"₹{price:,.2f}")
            m2.metric("📅 1D",       f"{change_1d:+.2f}%",  delta=f"{change_1d:+.2f}%")
            m3.metric("📆 5D",       f"{change_5d:+.2f}%",  delta=f"{change_5d:+.2f}%")
            m4.metric("🏢 Sector",   sd_data.get("sector", "N/A"))
            m5.metric(f"{s_emoji} Sentiment", overall_s[:10], f"{sent_score}/100")

            raw_candles = pd_data.get("data", [])
            if raw_candles:
                try:
                    dfc      = pd.DataFrame(raw_candles)
                    date_col = "Date" if "Date" in dfc.columns else "index"
                    fig_c    = go.Figure(go.Candlestick(
                        x=dfc[date_col], open=dfc["Open"], high=dfc["High"],
                        low=dfc["Low"],  close=dfc["Close"], name=resolved,
                        increasing_line_color="#00ff88", decreasing_line_color="#ff4444",
                        increasing_fillcolor="#00cc66",  decreasing_fillcolor="#cc2222",
                    ))
                    fig_c.update_layout(
                        title=dict(text=f"📈 {resolved} — 90-Day Candlestick Chart (NSE)",
                                   font=dict(color="#00d4ff", size=15)),
                        template="plotly_dark", height=430,
                        xaxis_rangeslider_visible=False,
                        paper_bgcolor="#080f1f", plot_bgcolor="#0a1020",
                        margin=dict(t=50, l=10, r=10, b=10),
                        xaxis=dict(gridcolor="#1a2a3a", linecolor="#1a2a3a"),
                        yaxis=dict(gridcolor="#1a2a3a", linecolor="#1a2a3a"),
                    )
                    st.plotly_chart(fig_c, use_container_width=True)
                except Exception as e:
                    st.warning(f"📉 Chart unavailable: {e}")

            left, right = st.columns(2)
            with left:
                st.markdown("<div class='result-title'>📈 Detected Chart Patterns</div>", unsafe_allow_html=True)
                pats = pd_data.get("patterns", [])
                if pats:
                    for p in pats:
                        sig   = p.get("signal", "NEUTRAL")
                        color = "#00ff88" if "BULL" in sig else "#ff4444" if "BEAR" in sig else "#ffcc00"
                        icon  = "🟢" if "BULL" in sig else "🔴" if "BEAR" in sig else "🟡"
                        conf  = int(p.get("confidence", 0.5) * 100)
                        st.markdown(
                            f"<div class='pattern-pill' style='border-color:{color}'>"
                            f"{icon} <b>{p.get('pattern','?')}</b> &nbsp;"
                            f"<span style='color:#5a7a96;font-size:.8rem'>{conf}% conf</span><br>"
                            f"<span style='color:#8ab0c8;font-size:.8rem'>{sig}</span>"
                            + (f"<br><span style='color:#5a7a96;font-size:.78rem'>{p.get('detail','')}</span>" if p.get('detail') else "")
                            + "</div>", unsafe_allow_html=True)
                else:
                    st.info("No strong patterns detected.")
            with right:
                st.markdown("<div class='result-title'>🎯 Opportunity Signals</div>", unsafe_allow_html=True)
                sigs = sd_data.get("signals", [])
                if sigs:
                    for s in sigs:
                        strength = s.get("strength", "LOW")
                        color    = "#00ff88" if strength == "HIGH" else "#ffcc00" if strength == "MEDIUM" else "#5a7a96"
                        icon     = "🔥" if strength == "HIGH" else "⚡" if strength == "MEDIUM" else "💤"
                        st.markdown(
                            f"<div class='sig-pill' style='border-color:{color}'>"
                            f"{icon} <b>{s.get('signal_type','?')}</b> &nbsp;"
                            f"<span style='color:{color};font-size:.78rem'>{strength}</span><br>"
                            f"<span style='color:#8ab0c8;font-size:.8rem'>{s.get('message','')}</span><br>"
                            f"<span style='color:{color};font-size:.8rem'>→ {s.get('action','')}</span>"
                            "</div>", unsafe_allow_html=True)
                else:
                    st.info("No opportunity signals.")

            fund = sd_data.get("fundamentals", {})
            if any(v for v in fund.values() if v is not None):
                st.markdown("")
                st.markdown("<div class='result-title'>📊 Key Fundamentals</div>", unsafe_allow_html=True)
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("P/E Ratio", fund.get("pe_ratio", "N/A"))
                f2.metric("Div Yield", f"{fund.get('div_yield','N/A')}%")
                f3.metric("52W High",  f"₹{fund.get('52w_high','N/A')}")
                f4.metric("52W Low",   f"₹{fund.get('52w_low','N/A')}")

            st.markdown("")
            st.markdown("<div class='result-title'>📰 News Sentiment</div>", unsafe_allow_html=True)
            ns1, ns2 = st.columns([1, 2])
            with ns1:
                st.metric(f"{s_emoji} Sentiment", overall_s, f"{sent_score}/100")
            with ns2:
                themes = sent_data.get("key_themes", [])
                if themes:
                    st.markdown("**Themes:** " + " • ".join(themes))
                analysis = sent_data.get("analysis", "")
                if analysis and "429" not in analysis and "quota" not in analysis.lower():
                    st.caption(analysis)
            with st.expander("📰 News Headlines"):
                headlines = sent_data.get("raw_news", [])
                shown = [n for n in headlines if n.get("title")]
                if shown:
                    for n in shown:
                        st.markdown(f"- [{n.get('title','')}]({n.get('url','#')}) — *{n.get('publisher','Unknown')}* ({n.get('date','')})")
                else:
                    st.info("No news headlines available for this stock right now.")

            st.markdown("---")
            st.markdown("<div class='result-title'>🧠 AI Market Brief</div>", unsafe_allow_html=True)
            expl = result.get("explanation", "")
            if expl and ("429" in expl or "quota" in expl.lower() or "AI analysis temporarily" in expl):
                expl = ""
            if expl:
                st.markdown(f"<div class='ai-card'>{expl}</div>", unsafe_allow_html=True)
            else:
                from agents.llm_router import offline_brief
                ob = offline_brief(ticker=resolved, pattern_data=pd_data,
                                   signal_data=sd_data, sentiment_data=sent_data)
                st.markdown(f"<div class='ai-card'>{ob}</div>", unsafe_allow_html=True)

            with st.expander("🤖 Agent Audit Trail", expanded=False):
                for log in result.get("step_log", []):
                    if "✅" in log:   st.success(log)
                    elif "❌" in log: st.error(log)
                    elif "⚠️" in log: st.warning(log)
                    else:             st.info(log)
        else:
            st.markdown(f"""
            <div style='background:rgba(255,68,68,.08);border:1px solid rgba(255,68,68,0.3);
            border-radius:14px;padding:24px'>
            ❌ <b>No NSE data found for "{raw_input.upper()}"</b><br><br>
            📌 Common corrections:<br>
            &nbsp;&nbsp;• INFOSYS → <b>INFY</b> &nbsp; • HDFC → <b>HDFCBANK</b> &nbsp; • SBI → <b>SBIN</b><br>
            &nbsp;&nbsp;• HCL → <b>HCLTECH</b> &nbsp; • L&T → <b>LT</b> &nbsp; • HUL → <b>HINDUNILVR</b><br><br>
            📖 Check the NSE Ticker Reference expander above.
            </div>""", unsafe_allow_html=True)
    elif not analyze_btn:
        st.markdown("""
        <div style='background:rgba(0,212,255,.04);border:1px dashed rgba(0,212,255,0.2);
        border-radius:14px;padding:32px;text-align:center;margin-top:8px'>
        <div style='font-size:2.5rem'>🔍</div>
        <div style='color:#a0c4d8;font-size:1.05rem;margin:10px 0 6px;font-weight:600'>
        Search any NSE-listed stock to begin analysis</div>
        <div style='color:#5a7a96;font-size:.85rem'>
        Supports all NSE stocks — Nifty 50, Nifty 200, SME, and beyond<br>
        Click a demo chip above or type any ticker / company name
        </div></div>""", unsafe_allow_html=True)
        with st.expander("🔬 What does each agent do?", expanded=False):
            st.markdown("""
1. 🔍 **PatternDetectorAgent** — RSI-14, MACD, Golden/Death Cross, Bollinger Bands, EMA 20/50
2. 📡 **SignalFinderAgent** — P/E, 52W proximity, dividend yield, market cap classification
3. 📰 **NewsSentimentAgent** — Gemini 2.0 Flash / Mistral-7B news analysis
4. 🧠 **ExplanationAgent** — AI brief (Gemini → HuggingFace → rule-engine offline)
5. 📊 **LangGraph Orchestrator** — coordinates all agents with full audit trail
            """)


# ════════ TAB 2 — SECTOR HEATMAP (3 charts)
with tab2:
    st.markdown("### 🌡️ NSE Sector Intelligence — Live Performance Dashboard")
    st.caption("40 NSE stocks across 8 sectors — 3 chart views for complete market picture")

    h_tab1, h_tab2, h_tab3 = st.tabs([
        "🌡️ Treemap (Market Cap)",
        "📊 Sector Bar Chart",
        "🔥 Top Movers",
    ])

    with h_tab1:
        st.info("⏱️ Loads 40 stocks live (20-30 sec). Block size = market cap. Color = % change today.")
        if st.button("🔄 Load Sector Treemap", type="primary", key="treemap_btn"):
            with st.spinner("Building live NSE treemap (8 sectors, 40 stocks)…"):
                try:
                    fig_heat = build_sector_heatmap()
                    st.plotly_chart(fig_heat, use_container_width=True)
                    col_a, col_b, col_c, col_d, col_e = st.columns(5)
                    col_a.markdown("🟥 **Dark Red** = Loss >2%")
                    col_b.markdown("🔴 **Red** = Loss")
                    col_c.markdown("⬛ **Dark** = Flat")
                    col_d.markdown("🟢 **Green** = Gain")
                    col_e.markdown("🟩 **Dark Green** = Gain >2%")
                except Exception as e:
                    st.error(f"Treemap error: {e}")

    with h_tab2:
        st.info("📊 Sector-level average % change today — instantly shows winners vs losers.")
        if st.button("🔄 Load Sector Bar Chart", type="primary", key="bar_btn"):
            with st.spinner("Fetching sector performance data…"):
                try:
                    fig_bar = build_sector_bar_chart()
                    st.plotly_chart(fig_bar, use_container_width=True)
                    st.caption("🟢 Green bars = sector gaining today | 🔴 Red bars = sector under pressure")
                except Exception as e:
                    st.error(f"Bar chart error: {e}")

    with h_tab3:
        st.info("🔥 Top 5 gainers vs top 5 losers across all 40 tracked NSE stocks — today.")
        if st.button("🔄 Load Top Movers", type="primary", key="movers_btn"):
            with st.spinner("Scanning 40 stocks for today's biggest movers…"):
                try:
                    fig_mv = build_top_movers_chart()
                    st.plotly_chart(fig_mv, use_container_width=True)
                    st.caption("🟢 Right side = today's top gainers | 🔴 Left side = today's top losers")
                except Exception as e:
                    st.error(f"Top movers error: {e}")


# ════════ TAB 3 — RACE CHART
with tab3:
    st.markdown("### 🏆 Nifty Top-10 Performance Race Chart")
    st.caption("AI Market Video Engine — animated, data-driven visual | Base = 100")
    st.info("🎥 StockSense AI's answer to the AI Market Video Engine sub-problem in PS #6")
    period_sel = st.selectbox("Time Period", ["6mo", "1y", "2y"], index=1,
        format_func=lambda x: {"6mo": "6 Months", "1y": "1 Year", "2y": "2 Years"}[x])
    if st.button("▶ Generate Race Chart", type="primary", key="race_btn"):
        with st.spinner("Building animated race chart from NSE historical data…"):
            try:
                fig_race = build_race_chart(period_sel)
                if fig_race.data:
                    st.plotly_chart(fig_race, use_container_width=True)
                    st.caption("▶ Press Play button on the chart to animate | Base = 100 at period start")
                else:
                    st.error("No data returned. Check internet connection.")
            except Exception as e:
                st.error(f"Race chart error: {e}")


# ════════ TAB 4 — FII/DII
with tab4:
    st.markdown("### 🏦 Smart Money Flow — FII/DII Institutional Tracker")
    st.caption("Track where Foreign & Domestic institutions are deploying or withdrawing capital")
    if st.button("📡 Fetch FII/DII Data", type="primary", key="fiidii_btn"):
        with st.spinner("Fetching institutional flow data…"):
            try:
                fii_data = fetch_fii_dii_data()
                signal   = get_smart_money_signal(fii_data)
                icon = "🟢" if "BUYING" in signal else "🔴" if "SELLING" in signal else "🟡"
                st.markdown(f"## {icon} {signal}")
                st.caption(f"Source: **{fii_data.get('source','NSE India')}**")
                records = fii_data.get("data", [])
                if records:
                    st.dataframe(pd.DataFrame(records[:12]), use_container_width=True, height=380)
            except Exception as e:
                st.error(f"FII/DII fetch error: {e}")
    with st.expander("📖 How to read FII/DII data"):
        st.markdown("""
| Signal | Meaning | Market Impact |
|---|---|---|
| 🟢 FII Net Buying | Foreign capital entering India | Bullish |
| 🔴 FII Net Selling | Foreign capital exiting India | Caution |
| 🟢 DII Net Buying | Domestic institutions absorbing sell-off | Support level |
| FII Sell + DII Buy | Mixed flows | Market finds support at lows |
| Both Buying | Strong institutional conviction | Strongly bullish |
        """)


# ════════ TAB 5 — IPO
with tab5:
    st.markdown("### 🚀 IPO Intelligence Center")
    st.caption("AI-powered verdict on every active/upcoming NSE IPO")
    if st.button("🔍 Scan IPO Pipeline", type="primary", key="ipo_btn"):
        with st.spinner("Scanning NSE IPO pipeline + generating AI verdicts…"):
            try:
                ipo_result = get_ipo_intelligence()
                ipos       = ipo_result.get("ipos", [])
                st.success(f"Found {ipo_result.get('count', 0)} IPO(s) in pipeline")
                if ipos:
                    for ipo in ipos:
                        with st.expander(
                            f"📋 {ipo.get('company','IPO')} | Opens: {ipo.get('open_date','TBA')}",
                            expanded=True,
                        ):
                            ic1, ic2, ic3, ic4 = st.columns(4)
                            ic1.metric("Price Band", ipo.get("price_band", "TBA"))
                            ic2.metric("GMP",        ipo.get("gmp", "N/A"))
                            ic3.metric("Issue Size", ipo.get("issue_size", "TBA"))
                            ic4.metric("Category",   ipo.get("category", "Mainboard"))
                            verdict = ipo.get("ai_verdict", "")
                            if verdict and "429" not in verdict and "quota" not in verdict.lower():
                                st.markdown("**🤖 AI Verdict:**")
                                if "STRONG SUBSCRIBE" in verdict: st.success(verdict)
                                elif "SUBSCRIBE" in verdict:      st.info(verdict)
                                elif "AVOID" in verdict:          st.error(verdict)
                                else:                              st.write(verdict)
                            else:
                                st.info("🤖 Rule-based verdict: Check GMP and subscription status for entry decision.")
                else:
                    st.info("No active IPOs right now. Check back during an IPO window.")
            except Exception as e:
                st.error(f"IPO error: {e}")


# ════════ TAB 6 — PORTFOLIO CHAT
with tab6:
    st.markdown("### 💬 Portfolio-Aware Market Chat")
    st.caption("Multi-step reasoning · portfolio-aware · source-cited responses")
    if not portfolio:
        st.info("💡 Add your NSE holdings in the sidebar for personalised portfolio analysis")
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
            "IT sector outlook this quarter?",
        ]
        sc = st.columns(2)
        for i, s in enumerate(suggestions):
            if sc[i % 2].button(s, key=f"sug_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": s})
                with st.spinner("Thinking…"):
                    resp = portfolio_chat(s, portfolio, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": resp})
                st.rerun()
    if prompt := st.chat_input("Ask about your portfolio or any NSE stock…"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analysing…"):
                response = portfolio_chat(prompt, portfolio, st.session_state.chat_history)
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ══ FOOTER
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#3a5a76;font-size:.8rem;padding:10px 0 20px'>
⚠️ StockSense AI is for educational purposes only. Not SEBI-registered investment advice.<br>
Always conduct your own due diligence and consult a SEBI-registered advisor before investing.<br>
<b style='color:#5a7a96'>Team NeuralForge</b> — ET GenAI Hackathon 2026 — Problem Statement #6
</div>""", unsafe_allow_html=True)
