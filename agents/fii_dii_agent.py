"""
FIIDIIAgent — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026

Fetches live FII/DII institutional flow data from NSE India public endpoint.
Tracks smart money to surface institutional sentiment signals.
"""

import requests
import yfinance as yf
import pandas as pd
from typing import Dict, Any, List


def fetch_fii_dii_data() -> Dict[str, Any]:
    """
    Fetch FII/DII trading activity from NSE India public API.
    Fallback: derive proxy signal from Nifty 50 price movement.
    Returns typed dict with data records, signal text, and source.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        url = "https://www.nseindia.com/api/fiidiiTradeReact"
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            records = data if isinstance(data, list) else data.get("data", [])
            if records:
                return {
                    "source": "NSE India (Live)",
                    "data": records[:15],
                    "status": "live"
                }
    except Exception as e:
        print(f"[FIIDIIAgent] NSE API error: {e}")

    # Fallback: derive from Nifty 50 daily movement
    return _build_nifty_proxy()


def _build_nifty_proxy() -> Dict[str, Any]:
    """Build estimated FII/DII data from Nifty 50 proxy via yfinance."""
    try:
        nifty = yf.download("^NSEI", period="1mo", progress=False, auto_adjust=True)
        if isinstance(nifty.columns, pd.MultiIndex):
            nifty.columns = [col[0] for col in nifty.columns]
        nifty = nifty.reset_index().tail(15)
        records = []
        for _, row in nifty.iterrows():
            try:
                daily_change = float(row["Close"]) - float(row["Open"])
                fii_net = round(daily_change * 45, 2)
                dii_net = round(abs(daily_change) * 25, 2)
                records.append({
                    "date": str(row["Date"])[:10],
                    "fii_net_cr": fii_net,
                    "dii_net_cr": dii_net,
                    "nifty_close": round(float(row["Close"]), 2)
                })
            except Exception:
                continue
        return {
            "source": "Nifty 50 Proxy (NSE API unavailable)",
            "data": records,
            "status": "estimated"
        }
    except Exception:
        return {"source": "Unavailable", "data": [], "status": "error"}


def get_smart_money_signal(fii_dii_data: Dict[str, Any]) -> str:
    """
    Analyze FII net flow trend over last 5 trading days.
    Returns human-readable signal string.
    """
    records = fii_dii_data.get("data", [])
    if not records:
        return "NEUTRAL — No FII/DII data available"

    try:
        fii_total = 0
        count = 0
        for r in records[:5]:
            val = (
                r.get("fii_net_cr") or
                r.get("FII_NET") or
                r.get("netVal") or
                r.get("NET_VALUE") or 0
            )
            try:
                fii_total += float(val)
                count += 1
            except Exception:
                continue

        if count == 0:
            return "NEUTRAL — Could not parse FII data"

        if fii_total > 3000:
            return f"🟢 STRONG FII BUYING — Net inflow of ₹{abs(fii_total):.0f} Cr in last 5 sessions. Bullish institutional sentiment."
        elif fii_total > 500:
            return f"🟡 FII NET BUYING — Moderate inflow of ₹{abs(fii_total):.0f} Cr. Market has institutional support."
        elif fii_total < -3000:
            return f"🔴 STRONG FII SELLING — Net outflow of ₹{abs(fii_total):.0f} Cr in last 5 sessions. Caution advised."
        elif fii_total < -500:
            return f"🟠 FII NET SELLING — Moderate outflow of ₹{abs(fii_total):.0f} Cr. Watch for DII support."
        else:
            return f"🟽 FII NEUTRAL — Mixed activity (₹{fii_total:.0f} Cr net). Market lacks directional conviction."
    except Exception as e:
        return f"NEUTRAL — Signal calculation error: {e}"


if __name__ == "__main__":
    print("Testing FIIDIIAgent...")
    data = fetch_fii_dii_data()
    print(f"Source: {data['source']} | Status: {data['status']}")
    print(f"Records: {len(data['data'])}")
    signal = get_smart_money_signal(data)
    print(f"Signal: {signal}")
