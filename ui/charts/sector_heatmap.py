"""
Sector Heatmap — StockSense AI | NeuralForge
Live NSE sector performance Plotly Treemap
Fixed: height, font size, label display, color scale visibility
"""
import yfinance as yf
import plotly.graph_objects as go
from typing import List

NSE_SECTORS = {
    "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "BPCL.NS"],
    "Auto": ["MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS"],
    "Pharma": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "APOLLOHOSP.NS"],
    "Metals": ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "COALINDIA.NS", "VEDL.NS"],
    "Infra": ["LT.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "GRASIM.NS", "SIEMENS.NS"],
}


def build_sector_heatmap() -> go.Figure:
    labels:  List[str]   = ["NSE Market"]
    parents: List[str]   = [""]
    values:  List[float] = [0]
    colors:  List[float] = [0]
    text:    List[str]   = ["NSE Market"]
    hovers:  List[str]   = ["<b>NSE Market Overview</b>"]

    for sector, stocks in NSE_SECTORS.items():
        sector_changes = []
        sector_val = 0.0

        for ticker in stocks:
            try:
                t    = yf.Ticker(ticker)
                fi   = t.fast_info
                last = float(fi.last_price)
                prev = float(fi.previous_close)
                chg  = round(((last - prev) / prev) * 100, 2)
                name = ticker.replace(".NS", "")
                mcap = float(getattr(fi, "market_cap", 0) or 0) / 1e10

                arrow = "\u25b2" if chg >= 0 else "\u25bc"
                display_text = f"{name}<br>{arrow}{abs(chg):.1f}%"

                labels.append(name)
                parents.append(sector)
                values.append(max(mcap, 2.0))
                colors.append(chg)
                text.append(display_text)
                hovers.append(
                    f"<b>{name}</b><br>"
                    f"Price: \u20b9{last:,.2f}<br>"
                    f"Change: {chg:+.2f}%<br>"
                    f"Sector: {sector}"
                )
                sector_changes.append(chg)
                sector_val += max(mcap, 2.0)
            except Exception:
                continue

        avg_chg = sum(sector_changes) / len(sector_changes) if sector_changes else 0.0
        arrow_s = "\u25b2" if avg_chg >= 0 else "\u25bc"

        labels.append(sector)
        parents.append("NSE Market")
        values.append(sector_val or 15.0)
        colors.append(avg_chg)
        text.append(f"<b>{sector}</b><br>{arrow_s}{abs(avg_chg):.1f}%")
        hovers.append(f"<b>{sector} Sector</b><br>Avg Change: {avg_chg:+.2f}%")

    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            text=text,
            customdata=hovers,
            hovertemplate="%{customdata}<extra></extra>",
            texttemplate="%{text}",
            textposition="middle center",
            marker=dict(
                colors=colors,
                colorscale=[
                    [0.0,  "#c0392b"],
                    [0.25, "#922b21"],
                    [0.5,  "#1c2833"],
                    [0.75, "#1e8449"],
                    [1.0,  "#27ae60"],
                ],
                cmid=0,
                showscale=True,
                colorbar=dict(
                    title=dict(text="% Change", font=dict(color="white", size=13)),
                    ticksuffix="%",
                    tickfont=dict(color="white"),
                    len=0.8,
                    thickness=16,
                ),
            ),
            textfont=dict(
                size=14,
                color="white",
                family="Arial Black, Arial, sans-serif",
            ),
            branchvalues="total",
            pathbar=dict(
                visible=True,
                edgeshape=">",
                thickness=24,
                textfont=dict(size=13, color="white"),
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text="\U0001f321\ufe0f NSE Sector Heatmap \u2014 Live Performance (8 Sectors | 40 Stocks)",
            font=dict(size=17, color="white"),
            x=0.01,
        ),
        paper_bgcolor="#070d1a",
        plot_bgcolor="#070d1a",
        height=640,
        margin=dict(t=60, l=5, r=5, b=10),
        font=dict(color="white"),
    )
    return fig


if __name__ == "__main__":
    fig = build_sector_heatmap()
    fig.show()
