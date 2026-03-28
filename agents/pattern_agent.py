"""
PatternDetectorAgent — StockSense AI | NeuralForge
ET GenAI Hackathon 2026 | PS #6

Pure pandas implementation of:
  RSI-14, MACD(12,26,9), Bollinger Bands(20,2),
  SMA-50, SMA-200, EMA-20, EMA-50
No pandas-ta / numba / llvmlite dependency.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Any, List


# ── Indicator helpers ────────────────────────────────────────────────────────

def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))


def _ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def _macd(series: pd.Series, fast=12, slow=26, signal=9):
    macd_line = _ema(series, fast) - _ema(series, slow)
    signal_line = _ema(macd_line, signal)
    return macd_line, signal_line


def _bollinger(series: pd.Series, period: int = 20, std: float = 2.0):
    mid = series.rolling(period).mean()
    sd = series.rolling(period).std()
    return mid + std * sd, mid - std * sd   # upper, lower


def _sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(period).mean()


# ── Data fetch ───────────────────────────────────────────────────────────────

def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    nse = ticker.upper()
    if not nse.endswith(".NS"):
        nse += ".NS"
    try:
        df = yf.download(nse, period=period, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        return df
    except Exception as e:
        print(f"[PatternAgent] yfinance error: {e}")
        return pd.DataFrame()


# ── Main detection ───────────────────────────────────────────────────────────

def detect_patterns(ticker: str) -> Dict[str, Any]:
    """
    Run full technical analysis on an NSE ticker.
    Returns patterns, confidence scores, price data (90-day OHLCV).
    """
    df = fetch_stock_data(ticker)
    if df.empty:
        df = fetch_stock_data(ticker, period="3mo")

    if df.empty or len(df) < 30:
        return {
            "ticker": ticker.upper().replace(".NS", ""),
            "current_price": 0,
            "price_change_1d": 0,
            "price_change_5d": 0,
            "volume": 0,
            "patterns": [{"pattern": "Data unavailable", "confidence": 0, "signal": "NEUTRAL", "detail": "Could not fetch NSE data."}],
            "data": [],
            "error": f"No data for {ticker}"
        }

    close = df["Close"].squeeze()

    # Compute all indicators
    rsi       = _rsi(close, 14)
    macd_l, macd_s = _macd(close)
    bb_upper, bb_lower = _bollinger(close)
    sma50     = _sma(close, 50)
    sma200    = _sma(close, 200)
    ema20     = _ema(close, 20)
    ema50     = _ema(close, 50)

    latest_idx = -1
    prev_idx   = -2

    def v(series, idx):   # safe scalar getter
        try:
            val = series.iloc[idx]
            return float(val) if pd.notna(val) else None
        except Exception:
            return None

    patterns_found: List[Dict] = []

    # ── RSI ──────────────────────────────────────────────────────────────────
    rsi_val = v(rsi, latest_idx)
    if rsi_val is not None:
        if rsi_val < 30:
            patterns_found.append({
                "pattern": "RSI Oversold",
                "confidence": 0.78,
                "signal": "BULLISH",
                "detail": f"RSI = {rsi_val:.1f} — below 30, potential reversal zone"
            })
        elif rsi_val > 70:
            patterns_found.append({
                "pattern": "RSI Overbought",
                "confidence": 0.75,
                "signal": "BEARISH",
                "detail": f"RSI = {rsi_val:.1f} — above 70, potential pullback zone"
            })

    # ── MACD Crossover ───────────────────────────────────────────────────────
    cm, cs = v(macd_l, latest_idx), v(macd_s, latest_idx)
    pm, ps = v(macd_l, prev_idx),   v(macd_s, prev_idx)
    if None not in (cm, cs, pm, ps):
        if pm < ps and cm > cs:
            patterns_found.append({
                "pattern": "MACD Bullish Crossover",
                "confidence": 0.82,
                "signal": "BULLISH",
                "detail": "MACD line crossed above signal — momentum turning positive"
            })
        elif pm > ps and cm < cs:
            patterns_found.append({
                "pattern": "MACD Bearish Crossover",
                "confidence": 0.80,
                "signal": "BEARISH",
                "detail": "MACD line crossed below signal — momentum turning negative"
            })

    # ── Golden / Death Cross ─────────────────────────────────────────────────
    c50, c200 = v(sma50, latest_idx), v(sma200, latest_idx)
    p50, p200 = v(sma50, prev_idx),   v(sma200, prev_idx)
    if None not in (c50, c200, p50, p200):
        if p50 < p200 and c50 > c200:
            patterns_found.append({
                "pattern": "Golden Cross",
                "confidence": 0.88,
                "signal": "STRONG BULLISH",
                "detail": "SMA-50 crossed above SMA-200 — major long-term bullish signal"
            })
        elif p50 > p200 and c50 < c200:
            patterns_found.append({
                "pattern": "Death Cross",
                "confidence": 0.87,
                "signal": "STRONG BEARISH",
                "detail": "SMA-50 crossed below SMA-200 — major long-term bearish signal"
            })

    # ── Bollinger Band Breakout ───────────────────────────────────────────────
    price_now = v(close, latest_idx)
    bbu = v(bb_upper, latest_idx)
    bbl = v(bb_lower, latest_idx)
    if None not in (price_now, bbu, bbl):
        if price_now > bbu:
            patterns_found.append({
                "pattern": "Bollinger Band Upper Breakout",
                "confidence": 0.73,
                "signal": "BULLISH BREAKOUT",
                "detail": f"Price ₹{price_now:,.2f} broke above upper band ₹{bbu:,.2f}"
            })
        elif price_now < bbl:
            patterns_found.append({
                "pattern": "Bollinger Band Lower Breakdown",
                "confidence": 0.72,
                "signal": "BEARISH BREAKDOWN",
                "detail": f"Price ₹{price_now:,.2f} broke below lower band ₹{bbl:,.2f}"
            })

    # ── EMA 20/50 Crossover ──────────────────────────────────────────────────
    ce20, ce50 = v(ema20, latest_idx), v(ema50, latest_idx)
    pe20, pe50 = v(ema20, prev_idx),   v(ema50, prev_idx)
    if None not in (ce20, ce50, pe20, pe50):
        if pe20 < pe50 and ce20 > ce50:
            patterns_found.append({
                "pattern": "EMA 20/50 Bullish Crossover",
                "confidence": 0.76,
                "signal": "BULLISH",
                "detail": "Short EMA crossed above medium EMA — upward momentum confirmed"
            })
        elif pe20 > pe50 and ce20 < ce50:
            patterns_found.append({
                "pattern": "EMA 20/50 Bearish Crossover",
                "confidence": 0.74,
                "signal": "BEARISH",
                "detail": "Short EMA crossed below medium EMA — downward momentum confirmed"
            })

    # ── Price changes ────────────────────────────────────────────────────────
    try:
        current_price  = float(df["Close"].iloc[-1])
        prev_close     = float(df["Close"].iloc[-2])
        close_5d_ago   = float(df["Close"].iloc[-6]) if len(df) >= 6 else prev_close
        change_1d = round(((current_price - prev_close)   / prev_close)   * 100, 2)
        change_5d = round(((current_price - close_5d_ago) / close_5d_ago) * 100, 2)
        volume    = int(df["Volume"].iloc[-1])
    except Exception:
        current_price = change_1d = change_5d = 0
        volume = 0

    if not patterns_found:
        patterns_found.append({
            "pattern": "No Strong Pattern Detected",
            "confidence": 0.50,
            "signal": "NEUTRAL",
            "detail": "Market is in consolidation — wait for a clearer setup."
        })

    return {
        "ticker":         ticker.upper().replace(".NS", ""),
        "current_price":  round(current_price, 2),
        "price_change_1d": change_1d,
        "price_change_5d": change_5d,
        "volume":         volume,
        "patterns":       patterns_found,
        "data":           df.tail(90).reset_index().to_dict("records")
    }


if __name__ == "__main__":
    result = detect_patterns("RELIANCE")
    print(f"Ticker : {result['ticker']}")
    print(f"Price  : ₹{result['current_price']} | 1D: {result['price_change_1d']}%")
    for p in result["patterns"]:
        print(f"  → {p['pattern']} ({p['signal']}) {int(p['confidence']*100)}%")
