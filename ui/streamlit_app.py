"""
StockSense AI — Main Streamlit Application
Team NeuralForge | ET GenAI Hackathon 2026 | PS #6 — AI for the Indian Investor
6 Tabs: Stock Analysis | Sector Heatmap | Race Chart | FII/DII | IPO | Portfolio Chat
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="StockSense AI | NeuralForge",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Lazy imports for speed ─────────────────────────────────────────────────────
from orchestrator.langgraph_flow import analyze_stock
from agents.portfolio_chat import portfolio_chat
from agents.fii_dii_agent import fetch_fii_dii_data, get_smart_money_signal
from agents.ipo_agent import get_ipo_intelligence
from agents.morning_briefing import generate_morning_briefing
from ui.charts.sector_heatmap import build_sector_heatmap
from ui.charts.race_chart import build_race_chart

# ── Morning Briefing (auto-generates on first load) ─────────────────────────
if "morning_briefing" not in st.session_state:
    with st.spinner("🌅 Generating today's AI market briefing..."):
        try:
            st.session_state.morning_briefing = generate_morning_briefing()
        except Exception as e:
            st.session_state.morning_briefing = (
                f"🌅 **Morning Briefing unavailable**: {str(e)}\n\n"
                "Please check your GOOGLE_API_KEY in Streamlit secrets."
            )

with st.expander("🌅 Today's AI Morning Briefing — tap to expand", expanded=False):
    st.markdown(st.session_state.morning_briefing)

st.markdown("---")

# ── Header ──────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.title("📈 StockSense AI")
    st.caption(
        "**Team NeuralForge** | ET GenAI Hackathon 2026 | Problem Statement #6"
    )
    st.caption(
        "7-Agent NSE Intelligence: Chart Patterns • Signals • FII/DII • IPOs • Sentiment • Chat"
    )
with col_h2:
    st.markdown("### 🤖 Agent Pipeline")
    st.code(
        "PatternDetector → SignalFinder\n"
        "→ SentimentAnalyzer → ExplainAgent\n"
        "→ PortfolioChat | FII/DII | IPO",
        language=None,
    )

st.markdown("---")

# ── Sidebar: Portfolio Input ───────────────────────────────────────────────
st.sidebar.title("🗂️ My Portfolio")
st.sidebar.caption("Add your NSE holdings for portfolio-aware analysis")

portfolio = []
num = st.sidebar.number_input(
    "Number of holdings", min_value=0, max_value=10, value=2, key="num_stocks"
)
for i in range(int(num)):
    c1, c2, c3 = st.sidebar.columns(3)
    t = c1.text_input(f"#{i+1} Ticker", key=f"t{i}", placeholder="TCS")
    q = c2.number_input("Qty", key=f"q{i}", min_value=0, value=10)
    p = c3.number_input("₹Avg", key=f"p{i}", min_value=0.0, value=1000.0)
    if t.strip():
        portfolio.append({"ticker": t.strip().upper(), "qty": q, "avg_price": p})

if portfolio:
    total_val = sum(h["qty"] * h["avg_price"] for h in portfolio)
    st.sidebar.metric("Portfolio Value (Cost)", f"₹{total_val:,.0f}")

st.sidebar.markdown("---")
st.sidebar.caption("🔒 Free stack: yfinance + Gemini + LangGraph")
st.sidebar.caption("🚀 Deployed free on Streamlit Cloud")
st.sidebar.caption("⚠️ Not SEBI-registered investment advice")

# ── 6 Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍 Stock Analysis",
    "🌡️ Sector Heatmap",
    "🏆 Race Chart",
    "🏦 FII/DII Tracker",
    "🚀 IPO Intelligence",
    "💬 Portfolio Chat",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 ─ STOCK ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("🔍 Multi-Agent Stock Analysis")
    st.caption(
        "4 AI agents run in sequence: Pattern Detection → Signal Finding → News Sentiment → AI Brief"
    )

    c1, c2 = st.columns([4, 1])
    with c1:
        ticker_input = st.text_input(
            "Enter NSE Ticker",
            placeholder="e.g. RELIANCE, HDFCBANK, TCS, INFY, WIPRO",
            key="main_ticker",
        )
    with c2:
        st.write("")
        st.write("")
        analyze_btn = st.button(
            "🚀 Analyze", type="primary", use_container_width=True
        )

    if analyze_btn and ticker_input.strip():
        ticker = ticker_input.strip().upper()
        with st.spinner(
            f"Running 4-agent LangGraph pipeline on {ticker}... (15–25 seconds)"
        ):
            result = analyze_stock(ticker)

        # Agent Audit Trail
        with st.expander(
            "🤖 Live Agent Activity Log — Multi-Agent Audit Trail", expanded=True
        ):
            for log in result.get("step_log", []):
                if "✅" in log:
                    st.success(log)
                elif "❌" in log:
                    st.error(log)
                elif "⚠️" in log:
                    st.warning(log)
                else:
                    st.info(log)

        pd_data = result.get("pattern_data") or {}
        sd_data = result.get("signal_data") or {}
        sent_data = result.get("sentiment_data") or {}

        if pd_data.get("current_price"):
            # Price metrics row
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("💰 Price", f"₹{pd_data['current_price']:,.2f}")
            m2.metric(
                "📅 1D Change",
                f"{pd_data['price_change_1d']:+.2f}%",
                delta=f"{pd_data['price_change_1d']:+.2f}%",
            )
            m3.metric(
                "📆 5D Change",
                f"{pd_data['price_change_5d']:+.2f}%",
                delta=f"{pd_data['price_change_5d']:+.2f}%",
            )
            m4.metric("🏢 Sector", sd_data.get("sector", "N/A"))
            sent_score = sent_data.get("sentiment_score", 50)
            sent_label = sent_data.get("overall_sentiment", "NEUTRAL")
            m5.metric("📰 Sentiment", f"{sent_label[:8]}", f"{sent_score}/100")

            # Candlestick chart
            raw = pd_data.get("data", [])
            if raw:
                try:
                    df_c = pd.DataFrame(raw)
                    date_col = "Date" if "Date" in df_c.columns else "index"
                    if date_col in df_c.columns:
                        fig_c = go.Figure(
                            go.Candlestick(
                                x=df_c[date_col],
                                open=df_c["Open"],
                                high=df_c["High"],
                                low=df_c["Low"],
                                close=df_c["Close"],
                                name=ticker,
                                increasing_line_color="#27ae60",
                                decreasing_line_color="#c0392b",
                            )
                        )
                        fig_c.update_layout(
                            title=f"📈 {ticker} — 90-Day Candlestick Chart (NSE)",
                            template="plotly_dark",
                            height=420,
                            xaxis_rangeslider_visible=False,
                            margin=dict(t=50, l=10, r=10, b=10),
                        )
                        st.plotly_chart(fig_c, use_container_width=True)
                except Exception as e:
                    st.warning(f"Chart rendering issue: {e}")

            # Patterns + Signals
            left, right = st.columns(2)
            with left:
                st.subheader("📈 Detected Chart Patterns")
                for p in pd_data.get("patterns", []):
                    sig = p.get("signal", "NEUTRAL")
                    icon = (
                        "🟢" if "BULL" in sig
                        else "🔴" if "BEAR" in sig
                        else "🟡"
                    )
                    conf = int(p.get("confidence", 0.5) * 100)
                    st.markdown(f"{icon} **{p['pattern']}**")
                    st.caption(
                        f"Confidence: {conf}% | Signal: {sig}"
                    )
                    if p.get("detail"):
                        st.caption(f"↳ {p['detail']}")
                    st.write("")

            with right:
                st.subheader("🎯 Opportunity Radar Signals")
                for s in sd_data.get("signals", []):
                    str_icon = (
                        "🔥" if s["strength"] == "HIGH"
                        else "⚡" if s["strength"] == "MEDIUM"
                        else "💤"
                    )
                    st.markdown(f"{str_icon} **{s['signal_type']}**")
                    st.caption(s["message"])
                    st.info(f"→ {s['action']}")
                    st.write("")

            # Fundamentals
            fund = sd_data.get("fundamentals", {})
            if any(fund.values()):
                st.subheader("📊 Key Fundamentals")
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("P/E Ratio", fund.get("pe_ratio", "N/A"))
                f2.metric("Div Yield", f"{fund.get('div_yield', 'N/A')}%")
                f3.metric("52W High", f"₹{fund.get('52w_high', 'N/A')}")
                f4.metric("52W Low", f"₹{fund.get('52w_low', 'N/A')}")

            # News Sentiment
            st.subheader("📰 News Sentiment Analysis")
            overall = sent_data.get("overall_sentiment", "NEUTRAL")
            s_icon = (
                "🟢" if "BULL" in overall
                else "🔴" if "BEAR" in overall
                else "🟡"
            )
            sc1, sc2 = st.columns([1, 2])
            with sc1:
                st.metric(
                    f"{s_icon} Sentiment", overall, f"Score: {sent_score}/100"
                )
            with sc2:
                themes = sent_data.get("key_themes", [])
                if themes:
                    st.markdown("**Key Themes:** " + " • ".join(themes))
                st.write(sent_data.get("analysis", ""))
                if sent_data.get("source_citations"):
                    st.caption(f"📎 Sources: {sent_data['source_citations']}")

            with st.expander("📰 Raw News Headlines"):
                for n in sent_data.get("raw_news", []):
                    st.markdown(
                        f"- **{n['title']}** — *{n['publisher']}* ({n['date']})"
                    )

            # AI Market Brief
            st.markdown("---")
            st.subheader("🧠 AI Market Brief")
            explanation = result.get("explanation", "")
            if explanation:
                st.markdown(explanation)

        else:
            st.error(
                f"Could not fetch data for '{ticker}'. "
                "Check the ticker symbol and try again."
            )
            st.info(
                "Examples: RELIANCE, HDFCBANK, TCS, INFY, WIPRO, SBIN, ITC, MARUTI"
            )

    elif not analyze_btn:
        st.info(
            "👆 Enter an NSE ticker above and click Analyze to run the full pipeline"
        )
        with st.expander("🔍 What happens when you click Analyze?"):
            st.markdown("""
1. 🔍 **PatternDetectorAgent** — fetches 90-day NSE OHLCV data, detects 5+ chart patterns (RSI, MACD, Golden Cross, Bollinger Bands, EMA)
2. 📡 **SignalFinderAgent** — scans fundamentals + NSE bulk deals for opportunity signals (P/E, 52-week proximity, dividend alerts)
3. 📰 **NewsSentimentAgent** — analyzes latest news headlines via Gemini 1.5 Flash with source citations
4. 🧠 **ExplanationAgent** — synthesizes everything into a plain-English AI market brief with SEBI disclaimer
5. 📊 **Candlestick Chart** — interactive 90-day Plotly dark-theme chart rendered live

All coordinated by **LangGraph StateGraph** with a full audit trail visible above.
            """)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 ─ SECTOR HEATMAP
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🌡️ NSE Sector Heatmap — Live Performance")
    st.caption(
        "Size = Market Cap weight | Color = % change today | "
        "Data: live from NSE via yfinance"
    )
    st.warning(
        "⏱️ Loading takes 20–30 seconds — fetching live data for 40 NSE stocks across 8 sectors"
    )
    if st.button(
        "🔄 Load Live Sector Heatmap", type="primary", key="heatmap_btn"
    ):
        with st.spinner("Fetching live data for 8 sectors, 40 stocks..."):
            try:
                fig_heat = build_sector_heatmap()
                st.plotly_chart(fig_heat, use_container_width=True)
                st.caption(
                    "🟢 Green = Gaining today | 🔴 Red = Losing today | Size = market cap weight"
                )
            except Exception as e:
                st.error(f"Heatmap error: {e}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 ─ RACE CHART
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🏆 Nifty Top-10 Performance Race Chart")
    st.caption(
        "AI Market Video Engine — animated visualization of Nifty top-10 performance over time"
    )
    st.info(
        "🎥 This is StockSense AI's answer to the **AI Market Video Engine** sub-problem — "
        "a fully animated, data-driven visual market update"
    )
    period_sel = st.selectbox(
        "Select Time Period",
        options=["6mo", "1y", "2y"],
        index=1,
        format_func=lambda x: {"6mo": "6 Months", "1y": "1 Year", "2y": "2 Years"}[x],
    )
    if st.button("▶ Generate Race Chart", type="primary", key="race_btn"):
        with st.spinner("Building animated race chart from NSE historical data..."):
            try:
                fig_race = build_race_chart(period_sel)
                if fig_race.data:
                    st.plotly_chart(fig_race, use_container_width=True)
                    st.caption(
                        "Press ▶ Play on the chart to start the animation | "
                        "Base = 100 at start of selected period"
                    )
                else:
                    st.error("Could not fetch data for race chart. Please try again.")
            except Exception as e:
                st.error(f"Race chart error: {e}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 ─ FII/DII TRACKER
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("🏦 Smart Money Flow — FII/DII Institutional Tracker")
    st.caption(
        "Track where Foreign & Domestic institutions are deploying — or withdrawing — capital"
    )
    if st.button("📡 Fetch FII/DII Data", type="primary", key="fiidii_btn"):
        with st.spinner("Connecting to NSE India FII/DII data feed..."):
            try:
                fii_data = fetch_fii_dii_data()
                signal = get_smart_money_signal(fii_data)

                signal_icon = (
                    "🟢" if "BUYING" in signal
                    else "🔴" if "SELLING" in signal
                    else "🟡"
                )
                st.markdown(f"## {signal_icon} {signal}")
                st.caption(f"📡 Source: **{fii_data.get('source', 'NSE India')}**")

                records = fii_data.get("data", [])
                if records:
                    try:
                        df_fii = pd.DataFrame(records[:12])
                        st.dataframe(df_fii, use_container_width=True, height=380)
                    except Exception:
                        st.json(records[:5])
            except Exception as e:
                st.error(f"FII/DII error: {e}")

    st.markdown("---")
    with st.expander("📖 How to Read FII/DII Smart Money Data"):
        st.markdown("""
| Signal | Meaning | Market Impact |
|---|---|---|
| 🟢 FII Net Buying | Foreign money entering India | Bullish — confirms market strength |
| 🔴 FII Net Selling | Foreign money exiting India | Caution — potential downside |
| 🟢 DII Net Buying | Domestic institutions absorbing | Support — market holds levels |
| FII Sells + DII Buys | Mixed flow | Market likely to find support at lows |
| Both Buying | Strong conviction | Strong bullish confirmation |
        """)


# ════════════════════════════════════════════════════════════════════════════
# TAB 5 ─ IPO INTELLIGENCE
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🚀 IPO Intelligence Center")
    st.caption(
        "AI-powered IPO analysis — Gemini 1.5 Flash verdict on every active/upcoming NSE IPO"
    )
    if st.button("🔍 Scan IPO Pipeline", type="primary", key="ipo_btn"):
        with st.spinner(
            "Scanning NSE IPO pipeline + generating Gemini AI verdicts..."
        ):
            try:
                ipo_result = get_ipo_intelligence()
                ipos = ipo_result.get("ipos", [])
                st.success(f"Found {ipo_result.get('count', 0)} IPO(s) in pipeline")

                if ipos:
                    for ipo in ipos:
                        company = ipo.get("company", "Unknown IPO")
                        open_d = ipo.get("open_date", "TBA")
                        with st.expander(
                            f"📋 {company} | Opens: {open_d}", expanded=True
                        ):
                            ic1, ic2, ic3, ic4 = st.columns(4)
                            ic1.metric("Price Band", ipo.get("price_band", "TBA"))
                            ic2.metric("GMP", ipo.get("gmp", "N/A"))
                            ic3.metric("Issue Size", ipo.get("issue_size", "TBA"))
                            ic4.metric("Category", ipo.get("category", "Mainboard"))

                            verdict = ipo.get("ai_verdict", "Verdict unavailable")
                            st.markdown("**🤖 AI Investment Verdict:**")
                            if "STRONG SUBSCRIBE" in verdict:
                                st.success(verdict)
                            elif "SUBSCRIBE" in verdict:
                                st.info(verdict)
                            elif "AVOID" in verdict:
                                st.error(verdict)
                            else:
                                st.write(verdict)
                else:
                    st.info(
                        "No active IPOs found at this time. Check back during IPO window."
                    )
            except Exception as e:
                st.error(f"IPO Intelligence error: {e}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 6 ─ PORTFOLIO CHAT
# ════════════════════════════════════════════════════════════════════════════
with tab6:
    st.subheader("💬 Portfolio-Aware Market Chat")
    st.caption(
        "Next-Gen Market ChatGPT — portfolio-aware, source-cited, multi-step responses"
    )

    if not portfolio:
        st.info(
            "💡 Add your holdings in the sidebar for personalized, portfolio-aware answers"
        )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Starter suggestions (only when no history)
    if not st.session_state.chat_history:
        st.markdown("**💡 Try asking:**")
        suggestions = [
            "Which sector should I overweight in 2026?",
            "Should I buy Reliance at current levels?",
            "How to build a defensive portfolio for correction?",
            "Outlook for IT stocks this quarter?",
        ]
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            if cols[i % 2].button(s, key=f"sug_{i}"):
                st.session_state.chat_history.append({"role": "user", "content": s})
                with st.spinner("Thinking..."):
                    resp = portfolio_chat(
                        s, portfolio, st.session_state.chat_history
                    )
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": resp}
                )
                st.rerun()

    # Chat input
    if prompt := st.chat_input(
        "Ask about your portfolio, any NSE stock, or market trends..."
    ):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your portfolio and market data..."):
                response = portfolio_chat(
                    prompt, portfolio, st.session_state.chat_history
                )
            st.markdown(response)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ── Footer ─────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "⚠️ StockSense AI is for educational purposes only. "
    "Not SEBI-registered investment advice. Always do your own research before investing. | "
    "**Team NeuralForge** | ET GenAI Hackathon 2026 | PS #6"
)
