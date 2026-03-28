"""
PatternDetectorAgent — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026

Detects technical chart patterns on NSE stocks using yfinance + pandas-ta.
"""

import yfinance as yf
import pandas as pd
import pandas_ta as ta
from typing import Dict, Any, List


def fetch_stock_data(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """Fetch OHLCV data for any NSE ticker via yfinance."""
    nse_ticker = ticker.upper() + ".NS" if not ticker.upper().endswith(".NS") else ticker.upper()
    try:
        df = yf.download(nse_ticker, period=period, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]
        return df
    except Exception as e:
        print(f"[PatternAgent] yfinance error: {e}")
        return pd.DataFrame()


def detect_patterns(ticker: str) -> Dict[str, Any]:
    """
    Run technical analysis on a NSE ticker and return detected patterns.
    Detects: RSI, MACD crossover, Golden/Death Cross, Bollinger Bands, EMA.
    Returns typed dict with patterns, price data, and 90-day OHLCV.
    """
    df = fetch_stock_data(ticker)

    # Fallback: try 3-month data if 6-month fails
    if df.empty:
        df = fetch_stock_data(ticker, period="3mo")

    if df.empty:
        return {
            "ticker": ticker.upper(),
            "current_price": 0,
            "price_change_1d": 0,
            "price_change_5d": 0,
            "volume": 0,
            "patterns": [{"pattern": "Data unavailable", "confidence": 0, "signal": "NEUTRAL"}],
            "data": [],
            "error": f"Could not fetch data for {ticker}"
        }

    # Apply indicators
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.bbands(length=20, append=True)
    df.ta.sma(length=50, append=True)
    df.ta.sma(length=200, append=True)
    df.ta.ema(length=20, append=True)
    df.ta.ema(length=50, append=True)

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    patterns_found: List[Dict] = []

    # --- RSI Analysis ---
    rsi_cols = [c for c in df.columns if str(c).startswith("RSI_")]
    if rsi_cols:
        rsi_val = float(latest[rsi_cols[0]])
        if rsi_val < 30:
            patterns_found.append({
                "pattern": "RSI Oversold",
                "confidence": 0.78,
                "signal": "BULLISH",
                "detail": f"RSI at {rsi_val:.1f} — strong buying zone below 30"
            })
        elif rsi_val > 70:
            patterns_found.append({
                "pattern": "RSI Overbought",
                "confidence": 0.75,
                "signal": "BEARISH",
                "detail": f"RSI at {rsi_val:.1f} — potential selling pressure above 70"
            })
        elif 40 <= rsi_val <= 60:
            patterns_found.append({
                "pattern": "RSI Neutral Zone",
                "confidence": 0.55,
                "signal": "NEUTRAL",
                "detail": f"RSI at {rsi_val:.1f} — no extreme signal"
            })

    # --- MACD Crossover ---
    macd_cols = [c for c in df.columns if "MACD" in str(c) and "MACDs" not in str(c) and "MACDh" not in str(c)]
    macd_signal_cols = [c for c in df.columns if "MACDs_" in str(c)]
    if macd_cols and macd_signal_cols:
        try:
            curr_macd = float(latest[macd_cols[0]])
            curr_sig = float(latest[macd_signal_cols[0]])
            prev_macd = float(prev[macd_cols[0]])
            prev_sig = float(prev[macd_signal_cols[0]])
            if prev_macd < prev_sig and curr_macd > curr_sig:
                patterns_found.append({
                    "pattern": "MACD Bullish Crossover",
                    "confidence": 0.82,
                    "signal": "BULLISH",
                    "detail": "MACD line crossed above signal line — momentum turning up"
                })
            elif prev_macd > prev_sig and curr_macd < curr_sig:
                patterns_found.append({
                    "pattern": "MACD Bearish Crossover",
                    "confidence": 0.80,
                    "signal": "BEARISH",
                    "detail": "MACD line crossed below signal line — momentum turning down"
                })
        except Exception:
            pass

    # --- Golden Cross / Death Cross ---
    sma50_cols = [c for c in df.columns if "SMA_50" in str(c)]
    sma200_cols = [c for c in df.columns if "SMA_200" in str(c)]
    if sma50_cols and sma200_cols:
        try:
            curr_50 = float(latest[sma50_cols[0]])
            curr_200 = float(latest[sma200_cols[0]])
            prev_50 = float(prev[sma50_cols[0]])
            prev_200 = float(prev[sma200_cols[0]])
            if prev_50 < prev_200 and curr_50 > curr_200:
                patterns_found.append({
                    "pattern": "Golden Cross",
                    "confidence": 0.88,
                    "signal": "STRONG BULLISH",
                    "detail": "50-day MA crossed above 200-day MA — long-term bullish signal"
                })
            elif prev_50 > prev_200 and curr_50 < curr_200:
                patterns_found.append({
                    "pattern": "Death Cross",
                    "confidence": 0.87,
                    "signal": "STRONG BEARISH",
                    "detail": "50-day MA crossed below 200-day MA — long-term bearish signal"
                })
        except Exception:
            pass

    # --- Bollinger Band Breakout ---
    bb_upper_cols = [c for c in df.columns if "BBU_" in str(c)]
    bb_lower_cols = [c for c in df.columns if "BBL_" in str(c)]
    if bb_upper_cols and bb_lower_cols:
        try:
            close_price = float(latest["Close"])
            bb_upper = float(latest[bb_upper_cols[0]])
            bb_lower = float(latest[bb_lower_cols[0]])
            if close_price > bb_upper:
                patterns_found.append({
                    "pattern": "Bollinger Band Upper Breakout",
                    "confidence": 0.73,
                    "signal": "BULLISH BREAKOUT",
                    "detail": f"Price ₹{close_price:.2f} broke above upper band ₹{bb_upper:.2f}"
                })
            elif close_price < bb_lower:
                patterns_found.append({
                    "pattern": "Bollinger Band Lower Breakdown",
                    "confidence": 0.72,
                    "signal": "BEARISH BREAKDOWN",
                    "detail": f"Price ₹{close_price:.2f} broke below lower band ₹{bb_lower:.2f}"
                })
        except Exception:
            pass

    # --- EMA Crossover ---
    ema20_cols = [c for c in df.columns if "EMA_20" in str(c)]
    ema50_cols = [c for c in df.columns if "EMA_50" in str(c)]
    if ema20_cols and ema50_cols:
        try:
            curr_e20 = float(latest[ema20_cols[0]])
            curr_e50 = float(latest[ema50_cols[0]])
            prev_e20 = float(prev[ema20_cols[0]])
            prev_e50 = float(prev[ema50_cols[0]])
            if prev_e20 < prev_e50 and curr_e20 > curr_e50:
                patterns_found.append({
                    "pattern": "EMA 20/50 Bullish Crossover",
                    "confidence": 0.76,
                    "signal": "BULLISH",
                    "detail": "Short-term EMA crossed above medium-term EMA"
                })
            elif prev_e20 > prev_e50 and curr_e20 < curr_e50:
                patterns_found.append({
                    "pattern": "EMA 20/50 Bearish Crossover",
                    "confidence": 0.74,
                    "signal": "BEARISH",
                    "detail": "Short-term EMA crossed below medium-term EMA"
                })
        except Exception:
            pass

    # Calculate price changes
    try:
        current_price = float(latest["Close"])
        prev_close = float(prev["Close"])
        price_change_1d = round(((current_price - prev_close) / prev_close) * 100, 2)
        week_start = float(df.iloc[-5]["Close"]) if len(df) >= 5 else prev_close
        price_change_5d = round(((current_price - week_start) / week_start) * 100, 2)
        volume = int(latest["Volume"]) if "Volume" in latest else 0
    except Exception:
        current_price = 0
        price_change_1d = 0
        price_change_5d = 0
        volume = 0

    if not patterns_found:
        patterns_found.append({
            "pattern": "No Strong Pattern Detected",
            "confidence": 0.50,
            "signal": "NEUTRAL",
            "detail": "Market is in a consolidation phase. Wait for a clearer signal."
        })

    return {
        "ticker": ticker.upper().replace(".NS", ""),
        "current_price": round(current_price, 2),
        "price_change_1d": price_change_1d,
        "price_change_5d": price_change_5d,
        "volume": volume,
        "patterns": patterns_found,
        "data": df.tail(90).reset_index().to_dict("records")
    }


if __name__ == "__main__":
    print("Testing PatternDetectorAgent with RELIANCE...")
    result = detect_patterns("RELIANCE")
    print(f"Ticker: {result['ticker']}")
    print(f"Price: ₹{result['current_price']} | 1D: {result['price_change_1d']}%")
    print(f"Patterns found: {len(result['patterns'])}")
    for p in result['patterns']:
        print(f"  - {p['pattern']} ({p['signal']}) | Confidence: {int(p['confidence']*100)}%")
