"""
Sector Heatmap — StockSense AI | NeuralForge
Live NSE sector performance Plotly Treemap
ET GenAI Hackathon 2026 | PS #6
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
    """
    Build a live NSE sector performance heatmap using Plotly Treemap.
    Size = market cap weight. Color = % change today.
    """
    labels: List[str] = ["NSE Market"]
    parents: List[str] = [""]
    values: List[float] = [0]
    colors: List[float] = [0]
    hovers: List[str] = ["NSE Overview"]

    for sector, stocks in NSE_SECTORS.items():
        sector_changes = []
        sector_val = 0.0

        for ticker in stocks:
            try:
                t = yf.Ticker(ticker)
                fi = t.fast_info
                last = float(fi.last_price)
                prev = float(fi.previous_close)
                change = round(((last - prev) / prev) * 100, 2)
                name = ticker.replace(".NS", "")
                mcap = float(getattr(fi, "market_cap", 0) or 0) / 1e10

                labels.append(name)
                parents.append(sector)
                values.append(max(mcap, 1.0))
                colors.append(change)
                hovers.append(
                    f"<b>{name}</b><br>₹{last:,.2f}<br>{change:+.2f}%"
                )
                sector_changes.append(change)
                sector_val += max(mcap, 1.0)
            except Exception:
                continue

        avg_change = (
            sum(sector_changes) / len(sector_changes) if sector_changes else 0.0
        )
        labels.append(sector)
        parents.append("NSE Market")
        values.append(sector_val or 10.0)
        colors.append(avg_change)
        hovers.append(
            f"<b>{sector}</b><br>Avg: {avg_change:+.2f}%"
        )

    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            customdata=hovers,
            hovertemplate="%{customdata}<extra></extra>",
            marker=dict(
                colors=colors,
                colorscale=[
                    [0.0, "#c0392b"],
                    [0.35, "#922b21"],
                    [0.5, "#1c2833"],
                    [0.65, "#1e8449"],
                    [1.0, "#27ae60"],
                ],
                cmid=0,
                showscale=True,
                colorbar=dict(
                    title="% Change",
                    ticksuffix="%",
                    len=0.8
                ),
            ),
            textfont=dict(size=13, color="white"),
            branchvalues="total",
        )
    )

    fig.update_layout(
        title="🌡️ NSE Sector Heatmap — Live Performance",
        template="plotly_dark",
        height=500,
        margin=dict(t=50, l=5, r=5, b=5),
    )
    return fig


if __name__ == "__main__":
    fig = build_sector_heatmap()
    fig.show()
