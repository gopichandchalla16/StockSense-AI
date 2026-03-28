"""
Race Chart Engine — StockSense AI | NeuralForge
Animated Plotly bar race: Nifty Top-10 performance normalized to 100
ET GenAI Hackathon 2026 | PS #6 — AI Market Video Engine
"""
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict

NIFTY_TOP10: Dict[str, str] = {
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "SBI": "SBIN.NS",
    "HUL": "HINDUNILVR.NS",
    "ITC": "ITC.NS",
    "Kotak Bank": "KOTAKBANK.NS",
    "L&T": "LT.NS",
}


def build_race_chart(period: str = "1y") -> go.Figure:
    """
    Build an animated Plotly bar race chart for Nifty Top-10 stocks.
    All stocks normalized to a base of 100 at the start of the period.
    Includes Play/Pause animation buttons.
    """
    all_data: Dict[str, pd.Series] = {}

    for name, ticker in NIFTY_TOP10.items():
        try:
            df = yf.download(
                ticker, period=period, progress=False, auto_adjust=True
            )
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            if not df.empty and "Close" in df.columns:
                monthly = df["Close"].resample("ME").last()
                if len(monthly) > 1:
                    normalized = (monthly / monthly.iloc[0]) * 100
                    all_data[name] = normalized
        except Exception:
            continue

    if not all_data:
        fig = go.Figure()
        fig.update_layout(
            title="Race chart data unavailable — try again",
            template="plotly_dark",
            height=500,
        )
        return fig

    combined = pd.DataFrame(all_data).dropna(how="all").ffill()
    combined.index = combined.index.strftime("%b %Y")

    melted = combined.reset_index().melt(
        id_vars=["Date"], var_name="Stock", value_name="Performance"
    )
    melted["Performance"] = melted["Performance"].round(1)

    fig = px.bar(
        melted,
        x="Performance",
        y="Stock",
        animation_frame="Date",
        orientation="h",
        color="Stock",
        range_x=[50, 350],
        title="🏆 Nifty Top-10 Performance Race (Base = 100 at Start)",
        labels={
            "Performance": "Performance Index (Start = 100)",
            "Stock": "",
        },
        template="plotly_dark",
        height=500,
        text="Performance",
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
    )

    fig.update_layout(
        showlegend=False,
        yaxis={"categoryorder": "total ascending"},
        font=dict(size=13),
        margin=dict(t=60, l=10, r=10, b=10),
        updatemenus=[
            {
                "type": "buttons",
                "showactive": False,
                "y": 1.18,
                "x": 0.05,
                "buttons": [
                    {
                        "label": "▶ Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 700, "redraw": True},
                                "fromcurrent": True,
                            },
                        ],
                    },
                    {
                        "label": "⏸ Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {"frame": {"duration": 0}, "mode": "immediate"},
                        ],
                    },
                ],
            }
        ],
    )
    return fig


if __name__ == "__main__":
    fig = build_race_chart("1y")
    fig.show()
