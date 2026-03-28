"""
SignalFinderAgent — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026

Finds opportunity signals from NSE fundamentals, bulk deals, and market data.
Not a summarizer — a signal-finder.
"""

import requests
import yfinance as yf
from typing import Dict, Any, List


def fetch_bulk_deals(ticker: str) -> List[Dict]:
    """Attempt to fetch bulk deal data from NSE India public endpoint."""
    ticker_clean = ticker.upper().replace(".NS", "")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.nseindia.com/",
            "Accept-Language": "en-US,en;q=0.9",
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=8)
        url = "https://www.nseindia.com/api/bulk-deals"
        resp = session.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            deals = data.get("data", [])
            filtered = [d for d in deals if d.get("symbol", "").upper() == ticker_clean]
            return filtered[:5]
    except Exception:
        pass
    return []


def get_opportunity_signals(ticker: str) -> Dict[str, Any]:
    """
    Generate opportunity signals for a NSE ticker based on fundamentals.
    Detects: undervaluation, 52-week proximity, dividend opportunity.
    Returns typed dict with signals, fundamentals, company info.
    """
    nse_ticker = ticker.upper() + ".NS" if not ticker.upper().endswith(".NS") else ticker.upper()
    signals: List[Dict] = []
    info = {}

    try:
        stock = yf.Ticker(nse_ticker)
        info = stock.info
    except Exception as e:
        print(f"[SignalAgent] yfinance info error: {e}")

    # --- P/E Undervaluation Signal ---
    pe = info.get("trailingPE")
    if pe and isinstance(pe, (int, float)):
        if pe < 15:
            signals.append({
                "signal_type": "UNDERVALUATION ALERT",
                "message": f"P/E ratio of {round(pe, 1)} is below 15 — stock may be undervalued vs market average",
                "strength": "HIGH",
                "action": "Investigate for potential entry opportunity after further research"
            })
        elif pe > 50:
            signals.append({
                "signal_type": "OVERVALUATION WARNING",
                "message": f"P/E ratio of {round(pe, 1)} is above 50 — stock is trading at a significant premium",
                "strength": "MEDIUM",
                "action": "Exercise caution — growth must justify premium valuation"
            })

    # --- Dividend Yield Signal ---
    div_yield = info.get("dividendYield")
    if div_yield and isinstance(div_yield, (int, float)) and div_yield > 0:
        div_pct = round(div_yield * 100, 2)
        if div_pct > 4:
            signals.append({
                "signal_type": "HIGH DIVIDEND OPPORTUNITY",
                "message": f"Dividend yield of {div_pct}% exceeds 4% threshold — strong income stock",
                "strength": "HIGH",
                "action": "Consider for income-focused portfolio allocation"
            })
        elif div_pct > 2:
            signals.append({
                "signal_type": "DIVIDEND PAYING STOCK",
                "message": f"Dividend yield of {div_pct}% — moderate income opportunity",
                "strength": "MEDIUM",
                "action": "Good for conservative investors seeking stability"
            })

    # --- 52-Week Proximity Signal ---
    week52_high = info.get("fiftyTwoWeekHigh")
    week52_low = info.get("fiftyTwoWeekLow")
    current = info.get("currentPrice") or info.get("regularMarketPrice")
    if week52_high and week52_low and current:
        try:
            range_size = week52_high - week52_low
            if range_size > 0:
                pct_from_low = ((current - week52_low) / range_size) * 100
                if pct_from_low < 15:
                    signals.append({
                        "signal_type": "52-WEEK LOW PROXIMITY",
                        "message": f"Stock is within 15% of 52-week low ₹{round(week52_low, 2)} — potential value zone",
                        "strength": "HIGH",
                        "action": "Watch for volume confirmation before entry — potential reversal zone"
                    })
                elif pct_from_low > 85:
                    signals.append({
                        "signal_type": "52-WEEK HIGH PROXIMITY",
                        "message": f"Stock is near 52-week high ₹{round(week52_high, 2)} — momentum territory",
                        "strength": "MEDIUM",
                        "action": "Momentum play — check if breakout is backed by volume and fundamentals"
                    })
        except Exception:
            pass

    # --- Market Cap Signal ---
    market_cap = info.get("marketCap")
    if market_cap:
        if market_cap > 1e12:  # > 1 Lakh Crore
            cap_label = "Large Cap"
        elif market_cap > 2e10:  # > 20,000 Crore
            cap_label = "Mid Cap"
        else:
            cap_label = "Small Cap"
        signals.append({
            "signal_type": f"{cap_label.upper()} STOCK",
            "message": f"Market cap: ₹{round(market_cap/1e7, 0):.0f} Cr — classified as {cap_label}",
            "strength": "LOW",
            "action": f"Suitable for {cap_label.lower()} allocation in diversified portfolio"
        })

    bulk_deals = fetch_bulk_deals(ticker)

    if not signals:
        signals.append({
            "signal_type": "NO STRONG SIGNAL",
            "message": "No outstanding opportunity signals detected at current price levels",
            "strength": "LOW",
            "action": "Continue monitoring — wait for a clearer entry/exit trigger"
        })

    return {
        "ticker": ticker.upper().replace(".NS", ""),
        "company_name": info.get("longName", ticker.upper()),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": info.get("marketCap"),
        "signals": signals,
        "bulk_deals": bulk_deals,
        "fundamentals": {
            "pe_ratio": round(pe, 2) if pe else None,
            "div_yield_pct": round(div_yield * 100, 2) if div_yield else None,
            "52w_high": week52_high,
            "52w_low": week52_low,
            "current_price": current,
            "beta": info.get("beta"),
            "book_value": info.get("bookValue")
        }
    }


if __name__ == "__main__":
    print("Testing SignalFinderAgent with HDFCBANK...")
    result = get_opportunity_signals("HDFCBANK")
    print(f"Company: {result['company_name']} | Sector: {result['sector']}")
    print(f"Signals found: {len(result['signals'])}")
    for s in result['signals']:
        print(f"  [{s['strength']}] {s['signal_type']}: {s['message']}")
