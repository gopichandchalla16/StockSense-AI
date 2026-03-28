"""
Sector Heatmap — StockSense AI | NeuralForge
Live NSE sector performance — Plotly Treemap + Bar Chart
Fixes:
 - Hardcoded realistic market cap weights (fast_info.market_cap returns 0 often)
 - Bar chart fallback always visible
 - Bigger fonts, clearer labels, proper pathbar
ET GenAI Hackathon 2026 | PS #6
"""
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Tuple

# Realistic NSE market caps in ₹ Cr (as of early 2026, used as weights)
# These ensure blocks always render even if yfinance fast_info.market_cap = 0
HARDCODED_MCAP = {
    # IT
    "TCS":         1400000, "INFY": 600000, "WIPRO": 250000,
    "HCLTECH":      420000, "TECHM": 130000,
    # Banking
    "HDFCBANK":    1200000, "ICICIBANK": 750000, "SBIN": 700000,
    "KOTAKBANK":    380000, "AXISBANK": 360000,
    # Energy
    "RELIANCE":    1800000, "ONGC": 350000, "NTPC": 330000,
    "POWERGRID":   260000, "BPCL": 120000,
    # Auto
    "MARUTI":       380000, "TATAMOTORS": 290000, "BAJAJ-AUTO": 240000,
    "EICHERMOT":   120000, "HEROMOTOCO": 80000,
    # FMCG
    "HINDUNILVR":  560000, "ITC": 530000, "NESTLEIND": 210000,
    "BRITANNIA":   110000, "DABUR": 90000,
    # Pharma
    "SUNPHARMA":   380000, "CIPLA": 130000, "DRREDDY": 110000,
    "DIVISLAB":    100000, "APOLLOHOSP": 90000,
    # Metals
    "TATASTEEL":   170000, "HINDALCO": 140000, "JSWSTEEL": 200000,
    "COALINDIA":   240000, "VEDL": 170000,
    # Infra
    "LT":          520000, "ADANIPORTS": 260000, "ULTRACEMCO": 360000,
    "GRASIM":      160000, "SIEMENS": 200000,
}

NSE_SECTORS: Dict[str, List[str]] = {
    "IT":      ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "Energy":  ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "BPCL.NS"],
    "Auto":    ["MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS"],
    "FMCG":    ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS"],
    "Pharma":  ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "APOLLOHOSP.NS"],
    "Metals":  ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "COALINDIA.NS", "VEDL.NS"],
    "Infra":   ["LT.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "GRASIM.NS", "SIEMENS.NS"],
}

SECTOR_COLORS = {
    "IT": "#0066cc", "Banking": "#7b2ff7", "Energy": "#ff8c00",
    "Auto": "#00aa44", "FMCG": "#cc3300", "Pharma": "#00aaaa",
    "Metals": "#888888", "Infra": "#aa7700",
}


def _fetch_live_data() -> Tuple[Dict, Dict]:
    """Returns (prices, changes) dicts keyed by short ticker name."""
    prices  = {}
    changes = {}
    for sector, stocks in NSE_SECTORS.items():
        for ticker in stocks:
            name = ticker.replace(".NS", "")
            try:
                fi   = yf.Ticker(ticker).fast_info
                last = float(fi.last_price  or 0)
                prev = float(fi.previous_close or 0)
                chg  = round(((last - prev) / prev) * 100, 2) if prev else 0.0
                prices[name]  = round(last, 2)
                changes[name] = chg
            except Exception:
                prices[name]  = 0
                changes[name] = 0.0
    return prices, changes


def build_sector_heatmap() -> go.Figure:
    """Treemap: block size = hardcoded mcap weight, color = live % change."""
    prices, changes = _fetch_live_data()

    labels:  List[str]   = ["NSE"]
    parents: List[str]   = [""]
    values:  List[float] = [0]
    colors:  List[float] = [0.0]
    texts:   List[str]   = ["NSE Market"]
    hovers:  List[str]   = ["<b>NSE Market Overview</b>"]

    for sector, stocks in NSE_SECTORS.items():
        sector_chgs = []
        sector_val  = 0.0

        for ticker in stocks:
            name  = ticker.replace(".NS", "")
            chg   = changes.get(name, 0.0)
            price = prices.get(name, 0)
            mcap  = HARDCODED_MCAP.get(name, 50000)  # always > 0

            arrow = "\u25b2" if chg >= 0 else "\u25bc"
            sign  = "+" if chg >= 0 else ""

            labels.append(name)
            parents.append(sector)
            values.append(mcap)
            colors.append(chg)
            texts.append(f"<b>{name}</b><br>{arrow} {sign}{chg:.1f}%")
            hovers.append(
                f"<b>{name}</b><br>"
                + (f"Price: \u20b9{price:,.2f}<br>" if price else "")
                + f"Change: {sign}{chg:.2f}%<br>"
                + f"Sector: {sector}<br>"
                + f"Mcap: \u20b9{mcap//1000:,}K Cr"
            )
            sector_chgs.append(chg)
            sector_val  += mcap

        avg_chg = sum(sector_chgs) / len(sector_chgs) if sector_chgs else 0.0
        arrow_s = "\u25b2" if avg_chg >= 0 else "\u25bc"
        sign_s  = "+" if avg_chg >= 0 else ""

        labels.append(sector)
        parents.append("NSE")
        values.append(sector_val)
        colors.append(avg_chg)
        texts.append(f"<b>{sector}</b><br>{arrow_s} {sign_s}{avg_chg:.1f}%")
        hovers.append(f"<b>{sector} Sector</b><br>Avg: {sign_s}{avg_chg:.2f}%")

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        text=texts,
        customdata=hovers,
        hovertemplate="%{customdata}<extra></extra>",
        texttemplate="%{text}",
        textposition="middle center",
        marker=dict(
            colors=colors,
            colorscale=[
                [0.0,  "#8b0000"],
                [0.2,  "#c0392b"],
                [0.45, "#2c3e50"],
                [0.55, "#2c3e50"],
                [0.8,  "#1e8449"],
                [1.0,  "#006400"],
            ],
            cmid=0,
            cmin=-3,
            cmax=3,
            showscale=True,
            colorbar=dict(
                title=dict(text="% Change", font=dict(color="white", size=13)),
                ticksuffix="%",
                tickfont=dict(color="white", size=12),
                len=0.85,
                thickness=18,
                x=1.01,
            ),
        ),
        textfont=dict(
            size=13,
            color="white",
            family="Arial Black, Arial, sans-serif",
        ),
        branchvalues="total",
        pathbar=dict(
            visible=True,
            edgeshape=">",
            thickness=26,
            textfont=dict(size=13, color="white"),
        ),
        tiling=dict(packing="squarify", pad=3),
    ))

    fig.update_layout(
        title=dict(
            text="\U0001f321\ufe0f NSE Sector Heatmap \u2014 Live Performance (8 Sectors | 40 Stocks)",
            font=dict(size=17, color="white", family="Arial Black"),
            x=0.01,
        ),
        paper_bgcolor="#070d1a",
        plot_bgcolor="#070d1a",
        height=640,
        margin=dict(t=65, l=5, r=80, b=10),
        font=dict(color="white"),
    )
    return fig


def build_sector_bar_chart() -> go.Figure:
    """Bonus: Sector-level bar chart — always clearly visible."""
    _, changes = _fetch_live_data()

    sector_avgs = {}
    for sector, stocks in NSE_SECTORS.items():
        chgs = [changes.get(t.replace(".NS", ""), 0.0) for t in stocks]
        sector_avgs[sector] = round(sum(chgs) / len(chgs), 2) if chgs else 0.0

    sorted_sectors = sorted(sector_avgs.items(), key=lambda x: x[1], reverse=True)
    names  = [s[0] for s in sorted_sectors]
    values = [s[1] for s in sorted_sectors]
    colors = ["#27ae60" if v >= 0 else "#c0392b" for v in values]
    texts  = [f"{'+' if v >= 0 else ''}{v:.2f}%" for v in values]

    fig = go.Figure(go.Bar(
        x=names,
        y=values,
        text=texts,
        textposition="outside",
        textfont=dict(size=14, color="white", family="Arial Black"),
        marker=dict(
            color=colors,
            line=dict(color="rgba(255,255,255,0.2)", width=1),
        ),
        hovertemplate="<b>%{x}</b><br>Change: %{y:+.2f}%<extra></extra>",
    ))

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="rgba(255,255,255,0.3)",
        line_width=1,
    )

    fig.update_layout(
        title=dict(
            text="\U0001f4ca NSE Sector Performance — Today's Winners & Losers",
            font=dict(size=16, color="white", family="Arial Black"),
            x=0.01,
        ),
        paper_bgcolor="#070d1a",
        plot_bgcolor="#0a1020",
        height=420,
        margin=dict(t=60, l=10, r=10, b=40),
        xaxis=dict(
            tickfont=dict(size=14, color="white", family="Arial Black"),
            gridcolor="#1a2a3a",
            linecolor="#1a2a3a",
        ),
        yaxis=dict(
            title="% Change",
            ticksuffix="%",
            tickfont=dict(size=12, color="white"),
            gridcolor="#1a2a3a",
            linecolor="#1a2a3a",
            zeroline=False,
        ),
        font=dict(color="white"),
        showlegend=False,
    )
    return fig


def build_top_movers_chart(top_n: int = 10) -> go.Figure:
    """Bonus 2: Top N gainers and losers as a horizontal bar chart."""
    prices, changes = _fetch_live_data()
    all_stocks = [(name, chg) for name, chg in changes.items() if prices.get(name, 0) > 0]
    all_stocks.sort(key=lambda x: x[1])

    worst  = all_stocks[:5]
    best   = all_stocks[-5:][::-1]
    movers = best + worst

    names  = [m[0] for m in movers]
    values = [m[1] for m in movers]
    colors = ["#27ae60" if v >= 0 else "#c0392b" for v in values]
    texts  = [f"{'+' if v >= 0 else ''}{v:.2f}%" for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=names,
        orientation="h",
        text=texts,
        textposition="outside",
        textfont=dict(size=13, color="white"),
        marker=dict(
            color=colors,
            line=dict(color="rgba(255,255,255,0.15)", width=1),
        ),
        hovertemplate="<b>%{y}</b><br>%{x:+.2f}%<extra></extra>",
    ))

    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="rgba(255,255,255,0.3)",
        line_width=1,
    )

    fig.update_layout(
        title=dict(
            text="\U0001f525 Top 5 Gainers vs Top 5 Losers — Today",
            font=dict(size=16, color="white", family="Arial Black"),
            x=0.01,
        ),
        paper_bgcolor="#070d1a",
        plot_bgcolor="#0a1020",
        height=430,
        margin=dict(t=60, l=10, r=80, b=10),
        xaxis=dict(
            ticksuffix="%",
            tickfont=dict(size=12, color="white"),
            gridcolor="#1a2a3a",
            linecolor="#1a2a3a",
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(size=14, color="white", family="Arial Black"),
            gridcolor="#1a2a3a",
            linecolor="#1a2a3a",
        ),
        font=dict(color="white"),
        showlegend=False,
    )
    return fig


if __name__ == "__main__":
    build_sector_heatmap().show()
    build_sector_bar_chart().show()
    build_top_movers_chart().show()
