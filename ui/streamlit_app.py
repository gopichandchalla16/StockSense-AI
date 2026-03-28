"""
StockSense AI — Main Streamlit App
NeuralForge | ET GenAI Hackathon 2026 | Problem Statement #6
Judge-ready: Clean homepage, smart search, no ticker wall, resilient LLM
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

# ══════════════════════════ PRO CSS ══════════════════════════════════════
st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] { background: #070d1a; }

/* ── Hero banner ── */
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
.badge {
    display: inline-block; padding: 4px 13px; border-radius: 20px;
    font-size: 0.76rem; font-weight: 700; margin-right: 8px; letter-spacing: .4px;
}
.badge-blue   { background: rgba(0,212,255,0.12); color: #00d4ff; border: 1px solid #00d4ff40; }
.badge-purple { background: rgba(123,47,247,0.12); color: #a07cf7; border: 1px solid #7b2ff740; }
.badge-green  { background: rgba(0,255,136,0.12); color: #00ff88; border: 1px solid #00ff8840; }
.badge-live   { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid #00ff8855; animation: glow 2s infinite; }
@keyframes glow { 0%,100%{box-shadow:0 0 0 rgba(0,255,136,0)} 50%{box-shadow:0 0 10px rgba(0,255,136,.4)} }
.dot { display:inline-block; width:7px; height:7px; background:#00ff88;
       border-radius:50%; margin-right:5px; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.5)} }

/* ── Stat cards ── */
.stat-row { display:flex; gap:14px; margin:18px 0 10px; }
.stat-card {
    flex:1; background:linear-gradient(135deg,rgba(0,212,255,.06),rgba(123,47,247,.06));
    border:1px solid rgba(0,212,255,.18); border-radius:14px; padding:16px 20px; text-align:center;
}
.stat-val  { font-size:1.5rem; font-weight:800; color:#e8f4fc; margin:0; }
.stat-lbl  { font-size:.75rem; color:#5a7a96; margin:3px 0 0; font-weight:600; text-transform:uppercase; }

/* ── Pipeline ── */
.pipeline-wrap { display:flex; align-items:center; gap:6px; margin:10px 0 4px; overflow-x:auto; padding:4px 0; }
.pipe-step {
    background:rgba(255,255,255,.03); border:1px solid rgba(0,212,255,.2);
    border-radius:10px; padding:10px 14px; text-align:center; min-width:80px; flex-shrink:0;
}
.pipe-icon { font-size:1.3rem; }
.pipe-lbl  { font-size:.68rem; color:#a0c4d8; font-weight:600; margin-top:3px; line-height:1.3; }
.pipe-arr  { color:#7b2ff7; font-size:1.3rem; flex-shrink:0; }

/* ── Search area ── */
.search-card {
    background: rgba(255,255,255,.025);
    border: 1px solid rgba(0,212,255,.15);
    border-radius: 16px; padding: 22px 24px 16px; margin: 16px 0;
}
.chip-wrap { display:flex; gap:10px; margin-bottom:16px; flex-wrap:wrap; }

/* ── Market overview cards ── */
.mkt-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:16px 0; }
.mkt-card {
    background: #0c1830;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px; padding: 16px 18px;
}
.mkt-title { font-size:.78rem; color:#5a7a96; font-weight:700; text-transform:uppercase; margin:0 0 6px; }
.mkt-val   { font-size:1.15rem; font-weight:800; color:#e8f4fc; margin:0; }
.mkt-sub   { font-size:.75rem; color:#4a7090; margin:3px 0 0; }

/* ── Result area ── */
.result-title { color:#00d4ff; font-size:1rem; font-weight:700; margin:0 0 10px; }
.pattern-pill {
    border-left: 3px solid; border-radius: 0 10px 10px 0;
    padding: 10px 14px; margin: 6px 0;
    background: rgba(255,255,255,.03);
}
.sig-pill {
    border-left: 3px solid; border-radius: 0 10px 10px 0;
    padding: 10px 14px; margin: 6px 0;
    background: rgba(255,255,255,.03);
}
.ai-card {
    background: linear-gradient(135deg,rgba(0,212,255,.05),rgba(123,47,247,.05));
    border: 1px solid rgba(0,212,255,.18);
    border-radius: 14px; padding: 20px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] { font-weight:700; font-size:.88rem; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#0a1628; }
::-webkit-scrollbar-thumb { background:#00d4ff30; border-radius:3px; }

/* ── Streamlit tweaks ── */
[data-testid="stMetricValue"] { font-size:1.1rem !important; }
div[data-testid="stExpander"] { border:1px solid rgba(255,255,255,.07); border-radius:12px; }
</style>
""", unsafe_allow_html=True)

from orchestrator.langgraph_flow import analyze_stock
from agents.portfolio_chat   import portfolio_chat
from agents.fii_dii_agent    import fetch_fii_dii_data, get_smart_money_signal
from agents.ipo_agent        import get_ipo_intelligence
from agents.morning_briefing import generate_morning_briefing
from ui.charts.sector_heatmap import build_sector_heatmap
from ui.charts.race_chart     import build_race_chart
from utils.ticker_resolver    import resolve_ticker

# ══════════════════════════ HERO ════════════════════════════════════════
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

# ── Agent pipeline visual
st.markdown("")
st.markdown("<p style='color:#5a7a96;font-size:.8rem;font-weight:700;letter-spacing:1px;margin:0'>🤖 MULTI-AGENT PIPELINE</p>", unsafe_allow_html=True)
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

# ── Morning briefing (collapsed by default so homepage looks clean)
if "morning_briefing" not in st.session_state:
    try:
        st.session_state.morning_briefing = generate_morning_briefing()
    except Exception as e:
        st.session_state.morning_briefing = f"🌅 Market briefing unavailable: {e}"
with st.expander("🌅 Today's AI Morning Briefing — click to expand", expanded=False):
    st.markdown(st.session_state.morning_briefing)

st.markdown("---")

# ══════════════════════════ SIDEBAR ═════════════════════════════════════
st.sidebar.markdown("""
<div style='background:linear-gradient(135deg,#0a1628,#112040);padding:16px;
border-radius:12px;margin-bottom:14px;border:1px solid #00d4ff25'>
<h3 style='color:#00d4ff;margin:0 0 4px'>🗂️ My Portfolio</h3>
<p style='color:#5a7a96;font-size:.8rem;margin:0'>NSE holdings for AI-powered analysis</p></div>
""", unsafe_allow_html=True)
portfolio = []
num = st.sidebar.number_input("Holdings count", min_value=0, max_value=10, value=0, key="num_stocks")
for i in range(int(num)):
    c1, c2, c3 = st.sidebar.columns(3)
    t = c1.text_input(f"#{i+1} Ticker", key=f"t{i}", placeholder="TCS")
    q = c2.number_input("Qty",   key=f"q{i}", min_value=0, value=10)
    p = c3.number_input("₹Avg",  key=f"p{i}", min_value=0.0, value=1000.0, format="%.2f")
    if t.strip():
        portfolio.append({"ticker": t.strip().upper(), "qty": q, "avg_price": p})
if portfolio:
    st.sidebar.metric("💼 Portfolio Value", f"₹{sum(h['qty']*h['avg_price'] for h in portfolio):,.0f}")
st.sidebar.markdown("---")
st.sidebar.caption("🔒 Stack: yfinance · Gemini 2.0 Flash · HuggingFace Mistral · LangGraph")
st.sidebar.warning("⚠️ Not SEBI-registered investment advice")

# ══════════════════════════ TABS ════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Stock Analysis",
    "🌡️ Sector Heatmap",
    "🏆 Race Chart",
    "🏦 FII/DII Tracker",
    "🚀 IPO Intelligence",
    "💬 Portfolio Chat",
])

# ══════════════════════════ TAB 1 — STOCK ANALYSIS ══════════════════════
with tab1:

    # ── Section header
    st.markdown("")
    st.markdown("""
    <div style='background:linear-gradient(90deg,rgba(0,212,255,.08),transparent);
    border-left:3px solid #00d4ff;border-radius:0 8px 8px 0;padding:12px 18px;margin-bottom:8px'>
    <span style='color:#00d4ff;font-weight:800;font-size:1.05rem'>🔍 Multi-Agent Stock Analysis</span><br>
    <span style='color:#5a7a96;font-size:.85rem'>4 AI agents analyze any NSE stock in real-time — Pattern Detection → Signal Finding → News Sentiment → AI Brief</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Session state init
    if "selected_ticker" not in st.session_state:
        st.session_state.selected_ticker = ""
    if "search_stock" not in st.session_state:
        st.session_state.search_stock = ""

    # ── 3 clean demo chips (not 30 confusing buttons)
    st.markdown("<p style='color:#5a7a96;font-size:.8rem;font-weight:700;margin:8px 0 6px'>⚡ QUICK DEMO STOCKS</p>", unsafe_allow_html=True)
    chip_col1, chip_col2, chip_col3, chip_col4, chip_col5 = st.columns(5)

    def _set(t):
        st.session_state.selected_ticker = t
        st.session_state.search_stock    = t

    with chip_col1:
        if st.button("Reliance", use_container_width=True, on_click=_set, args=("RELIANCE",)):
            pass
    with chip_col2:
        if st.button("Infosys", use_container_width=True, on_click=_set, args=("INFY",)):
            pass
    with chip_col3:
        if st.button("HDFC Bank", use_container_width=True, on_click=_set, args=("HDFCBANK",)):
            pass
    with chip_col4:
        if st.button("TCS", use_container_width=True, on_click=_set, args=("TCS",)):
            pass
    with chip_col5:
        if st.button("Tata Motors", use_container_width=True, on_click=_set, args=("TATAMOTORS",)):
            pass

    # ── Smart search bar
    st.markdown("")
    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        ticker_input = st.text_input(
            "🔎 Search any NSE stock (ticker or company name)",
            value=st.session_state.get("search_stock", ""),
            placeholder="Type any NSE ticker: RELIANCE, INFY, HDFCBANK, TATAMOTORS, SUNPHARMA, IRCTC...",
            key="main_ticker_input",
        )
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        analyze_btn = st.button("🚀 Analyze", type="primary", use_container_width=True)

    # ── NSE reference collapsible (hidden by default — cleaner look)
    with st.expander("📖 NSE Ticker Reference — click to find any company symbol", expanded=False):
        st.markdown("""
| Company | Ticker | Company | Ticker | Company | Ticker |
|---|---|---|---|---|---|
| Reliance Industries | **RELIANCE** | Infosys | **INFY** | HDFC Bank | **HDFCBANK** |
| TCS | **TCS** | ICICI Bank | **ICICIBANK** | Axis Bank | **AXISBANK** |
| SBI | **SBIN** | Wipro | **WIPRO** | Bajaj Finance | **BAJFINANCE** |
| HCL Technologies | **HCLTECH** | Tech Mahindra | **TECHM** | Tata Motors | **TATAMOTORS** |
| Tata Steel | **TATASTEEL** | Maruti Suzuki | **MARUTI** | Sun Pharma | **SUNPHARMA** |
| Dr. Reddy's | **DRREDDY** | Cipla | **CIPLA** | Titan | **TITAN** |
| Bharti Airtel | **BHARTIARTL** | L&T | **LT** | NTPC | **NTPC** |
| ONGC | **ONGC** | Coal India | **COALINDIA** | ITC | **ITC** |
| Adani Ports | **ADANIPORTS** | Zomato | **ZOMATO** | Asian Paints | **ASIANPAINT** |
| HUL | **HINDUNILVR** | IRCTC | **IRCTC** | HAL | **HAL** |
| Bajaj Finserv | **BAJAJFINSV** | Nestle India | **NESTLEIND** | Pidilite | **PIDILITIND** |
| JSW Steel | **JSWSTEEL** | Tata Power | **TATAPOWER** | Havells | **HAVELLS** |
| Apollo Hospital | **APOLLOHOSP** | Divi's Labs | **DIVISLAB** | Berger Paints | **BERGEPAINT** |
| Nykaa | **FSN** | Paytm | **PAYTM** | Siemens | **SIEMENS** |
        """)

    # ══ ANALYSIS RESULTS ════════════════════════════════════════════════
    if analyze_btn and ticker_input.strip():
        raw_input   = ticker_input.strip()
        resolved, _ = resolve_ticker(raw_input)

        if resolved.upper() != raw_input.upper():
            st.info(f"✅ Auto-resolved **{raw_input.upper()}** → **{resolved}**")

        # Running banner
        st.markdown(f"""
        <div style='background:linear-gradient(90deg,rgba(0,212,255,.08),rgba(123,47,247,.08));
        border:1px solid #00d4ff30;border-radius:10px;padding:12px 20px;margin:10px 0'>
        🚀 Running <b>4-Agent LangGraph Pipeline</b> on
        <b style='color:#00d4ff'>{resolved}.NS</b> — fetching live NSE data & running AI analysis…
        </div>""", unsafe_allow_html=True)

        with st.spinner(f"Analyzing {resolved}…"):
            result = analyze_stock(raw_input)

        pd_data   = result.get("pattern_data")   or {}
        sd_data   = result.get("signal_data")     or {}
        sent_data = result.get("sentiment_data")  or {}
        price     = pd_data.get("current_price", 0)

        if price and price > 0:
            # ── Metric row
            change_1d  = pd_data.get("price_change_1d", 0)
            change_5d  = pd_data.get("price_change_5d", 0)
            sent_score = sent_data.get("sentiment_score", 50)
            overall_s  = sent_data.get("overall_sentiment", "NEUTRAL")
            s_emoji    = "🟢" if "BULL" in overall_s else "🔴" if "BEAR" in overall_s else "🟡"

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("💰 Price",       f"₹{price:,.2f}")
            m2.metric("📅 1D",          f"{change_1d:+.2f}%",  delta=f"{change_1d:+.2f}%")
            m3.metric("📆 5D",          f"{change_5d:+.2f}%",  delta=f"{change_5d:+.2f}%")
            m4.metric("🏢 Sector",      sd_data.get("sector", "N/A"))
            m5.metric(f"{s_emoji} Sentiment", overall_s[:10], f"{sent_score}/100")

            # ── Candlestick chart
            raw_candles = pd_data.get("data", [])
            if raw_candles:
                try:
                    dfc      = pd.DataFrame(raw_candles)
                    date_col = "Date" if "Date" in dfc.columns else "index"
                    fig_c    = go.Figure(go.Candlestick(
                        x=dfc[date_col],
                        open=dfc["Open"], high=dfc["High"],
                        low=dfc["Low"],   close=dfc["Close"],
                        name=resolved,
                        increasing_line_color="#00ff88",
                        decreasing_line_color="#ff4444",
                    ))
                    fig_c.update_layout(
                        title=dict(
                            text=f"📈 {resolved} — 90-Day Candlestick (NSE)",
                            font=dict(color="#00d4ff", size=15),
                        ),
                        template="plotly_dark",
                        height=430,
                        xaxis_rangeslider_visible=False,
                        paper_bgcolor="#080f1f",
                        plot_bgcolor="#080f1f",
                        margin=dict(t=50, l=10, r=10, b=10),
                        xaxis=dict(gridcolor="#ffffff0d"),
                        yaxis=dict(gridcolor="#ffffff0d"),
                    )
                    st.plotly_chart(fig_c, use_container_width=True)
                except Exception as e:
                    st.warning(f"Chart render error: {e}")

            # ── Patterns + Signals side-by-side
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
                            f"{icon} <b>{p['pattern']}</b> &nbsp;<span style='color:#5a7a96;font-size:.8rem'>{conf}% conf</span><br>"
                            f"<span style='color:#8ab0c8;font-size:.8rem'>{sig}</span>"
                            + (f"<br><span style='color:#5a7a96;font-size:.78rem'>{p.get('detail','')}</span>" if p.get('detail') else "")
                            + "</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No strong patterns detected for this period.")

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
                            f"{icon} <b>{s['signal_type']}</b> &nbsp;<span style='color:{color};font-size:.78rem'>{strength}</span><br>"
                            f"<span style='color:#8ab0c8;font-size:.8rem'>{s['message']}</span><br>"
                            f"<span style='color:{color};font-size:.8rem'>→ {s['action']}</span>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.info("No opportunity signals right now.")

            # ── Fundamentals row
            fund = sd_data.get("fundamentals", {})
            if any(v for v in fund.values() if v is not None):
                st.markdown("")
                st.markdown("<div class='result-title'>📊 Key Fundamentals</div>", unsafe_allow_html=True)
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("P/E Ratio", fund.get("pe_ratio", "N/A"))
                f2.metric("Div Yield", f"{fund.get('div_yield','N/A')}%")
                f3.metric("52W High",  f"₹{fund.get('52w_high','N/A')}")
                f4.metric("52W Low",   f"₹{fund.get('52w_low','N/A')}")

            # ── News sentiment
            st.markdown("")
            st.markdown("<div class='result-title'>📰 News Sentiment</div>", unsafe_allow_html=True)
            ns1, ns2 = st.columns([1, 2])
            with ns1:
                st.metric(f"{s_emoji} Sentiment", overall_s, f"{sent_score}/100")
            with ns2:
                themes = sent_data.get("key_themes", [])
                if themes:
                    st.markdown("**Themes:** " + " &bull; ".join(themes), unsafe_allow_html=True)
                st.caption(sent_data.get("analysis", ""))
            with st.expander("📰 News Headlines"):
                for n in sent_data.get("raw_news", []):
                    st.markdown(f"- [{n.get('title','')}]({n.get('url','#')}) — *{n.get('publisher','Unknown')}* ({n.get('date','')})",
                                unsafe_allow_html=False)

            # ── AI Brief (the star of the show)
            st.markdown("---")
            st.markdown("<div class='result-title'>🧠 AI Market Brief</div>", unsafe_allow_html=True)
            expl = result.get("explanation", "")
            if expl:
                st.markdown(
                    f"<div class='ai-card'>{expl}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.info("Brief unavailable for this stock.")

            # ── Agent audit trail (collapsed — keeps UI clean)
            with st.expander("🤖 Agent Audit Trail — click to inspect", expanded=False):
                for log in result.get("step_log", []):
                    if "✅" in log:   st.success(log)
                    elif "❌" in log: st.error(log)
                    elif "⚠️" in log: st.warning(log)
                    else:             st.info(log)

        else:
            # ── Error card
            st.markdown(f"""
            <div style='background:rgba(255,68,68,.08);border:1px solid #ff444440;
            border-radius:14px;padding:24px'>
            ❌ <b>No NSE data found for "{raw_input.upper()}"</b><br><br>
            📌 <b>Common corrections:</b><br>
            &nbsp;&nbsp;• INFOSYS → <b>INFY</b> &nbsp; • HDFC → <b>HDFCBANK</b> &nbsp; • SBI → <b>SBIN</b><br>
            &nbsp;&nbsp;• HCL → <b>HCLTECH</b> &nbsp; • L&T → <b>LT</b> &nbsp; • HUL → <b>HINDUNILVR</b><br><br>
            📖 Open the <b>NSE Ticker Reference</b> expander above to find the exact symbol.
            </div>""", unsafe_allow_html=True)

    elif not analyze_btn:
        # ── Welcome state — judges see this first
        st.markdown("""
        <div style='background:rgba(0,212,255,.04);border:1px dashed #00d4ff30;
        border-radius:14px;padding:32px;text-align:center;margin-top:8px'>
        <div style='font-size:2.5rem'>🔍</div>
        <div style='color:#a0c4d8;font-size:1.05rem;margin:10px 0 6px;font-weight:600'>
        Search any NSE-listed stock above to begin</div>
        <div style='color:#5a7a96;font-size:.85rem'>
        Supports all NSE stocks — Nifty 50, Nifty 200, SME, and beyond<br>
        Type a ticker like <b>RELIANCE</b> or a company name like <b>Infosys</b>
        </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        with st.expander("🔬 What does each agent do?", expanded=False):
            st.markdown("""
1. 🔍 **PatternDetectorAgent** — RSI-14, MACD(12,26,9), Golden/Death Cross, Bollinger Bands, EMA 20/50
2. 📡 **SignalFinderAgent** — P/E ratio, 52W proximity, dividend yield, bulk deal signals
3. 📰 **NewsSentimentAgent** — Gemini 2.0 Flash / Mistral-7B real-time news analysis
4. 🧠 **ExplanationAgent** — Plain English AI brief (Gemini → HuggingFace → offline rule-engine)
5. 📊 **LangGraph Orchestrator** — coordinates all agents with full audit trail
            """)


# ══════════════════════════ TAB 2 — SECTOR HEATMAP ══════════════════════
with tab2:
    st.markdown("### 🌡️ NSE Sector Heatmap — Live Performance")
    st.caption("Size = Market Cap weight | Color = % change today | 40 stocks × 8 sectors")
    st.warning("⏱️ Loading takes 20–30 seconds — fetching live data for 40 NSE stocks")
    if st.button("🔄 Load Live Heatmap", type="primary", key="heatmap_btn"):
        with st.spinner("Fetching live sector data…"):
            try:
                st.plotly_chart(build_sector_heatmap(), use_container_width=True)
                st.caption("🟢 Green = gaining | 🔴 Red = losing | Block size = market cap weight")
            except Exception as e:
                st.error(f"Heatmap error: {e}")


# ══════════════════════════ TAB 3 — RACE CHART ══════════════════════════
with tab3:
    st.markdown("### 🏆 Nifty Top-10 Performance Race Chart")
    st.caption("AI Market Video Engine — animated, data-driven | Base = 100")
    st.info("🎥 StockSense AI's answer to the AI Market Video Engine sub-problem")
    period_sel = st.selectbox("Time Period", ["6mo", "1y", "2y"], index=1,
        format_func=lambda x: {"6mo": "6 Months", "1y": "1 Year", "2y": "2 Years"}[x])
    if st.button("▶ Generate Race Chart", type="primary", key="race_btn"):
        with st.spinner("Building animated race chart from NSE historical data…"):
            try:
                fig_race = build_race_chart(period_sel)
                if fig_race.data:
                    st.plotly_chart(fig_race, use_container_width=True)
                    st.caption("▶ Press Play to animate | Base = 100 at period start")
                else:
                    st.error("No data returned. Try again.")
            except Exception as e:
                st.error(f"Race chart error: {e}")


# ══════════════════════════ TAB 4 — FII/DII ═════════════════════════════
with tab4:
    st.markdown("### 🏦 Smart Money Flow — FII/DII Institutional Tracker")
    st.caption("Track where Foreign & Domestic institutions are deploying or withdrawing capital")
    if st.button("📡 Fetch FII/DII Data", type="primary", key="fiidii_btn"):
        with st.spinner("Connecting to NSE institutional data…"):
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
                st.error(f"FII/DII: {e}")
    with st.expander("📖 How to read FII/DII data"):
        st.markdown("""
| Signal | Meaning | Market Impact |
|---|---|---|
| 🟢 FII Net Buying | Foreign capital entering India | Bullish |
| 🔴 FII Net Selling | Foreign capital exiting India | Caution |
| 🟢 DII Net Buying | Domestic institutions absorbing sell-off | Support |
| FII Sell + DII Buy | Mixed flows | Market finds support at lows |
| Both Buying | Strong conviction from all institutions | Strongly bullish |
        """)


# ══════════════════════════ TAB 5 — IPO ═════════════════════════════════
with tab5:
    st.markdown("### 🚀 IPO Intelligence Center")
    st.caption("AI-powered IPO analysis — Gemini 2.0 Flash verdict on every active/upcoming NSE IPO")
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
                            verdict = ipo.get("ai_verdict", "Unavailable")
                            st.markdown("**🤖 AI Verdict:**")
                            if "STRONG SUBSCRIBE" in verdict: st.success(verdict)
                            elif "SUBSCRIBE" in verdict:      st.info(verdict)
                            elif "AVOID" in verdict:          st.error(verdict)
                            else:                              st.write(verdict)
                else:
                    st.info("No active IPOs right now. Check back during an IPO window.")
            except Exception as e:
                st.error(f"IPO error: {e}")


# ══════════════════════════ TAB 6 — PORTFOLIO CHAT ══════════════════════
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


# ══════════════════════════ FOOTER ══════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#3a5a76;font-size:.8rem;padding:10px 0 20px'>
⚠️ StockSense AI is for educational purposes only. Not SEBI-registered investment advice.<br>
Always conduct your own due diligence and consult a SEBI-registered advisor before investing.<br>
<b style='color:#5a7a96'>Team NeuralForge</b> — ET GenAI Hackathon 2026 — Problem Statement #6
</div>""", unsafe_allow_html=True)
