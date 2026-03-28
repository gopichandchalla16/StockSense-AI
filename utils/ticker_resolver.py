"""
Ticker Resolver — StockSense AI | NeuralForge
Maps common company names / wrong inputs to correct NSE tickers.
"""

# Map: anything user might type → correct NSE ticker symbol
TICKER_MAP = {
    # Full names
    "INFOSYS":           "INFY",
    "INFOSYS LIMITED":   "INFY",
    "TATA CONSULTANCY":  "TCS",
    "TCS":               "TCS",
    "HDFC BANK":         "HDFCBANK",
    "HDFCBANK":          "HDFCBANK",
    "HDFC":              "HDFCBANK",
    "RELIANCE":          "RELIANCE",
    "RELIANCE INDUSTRIES": "RELIANCE",
    "RIL":               "RELIANCE",
    "WIPRO":             "WIPRO",
    "ICICI":             "ICICIBANK",
    "ICICI BANK":        "ICICIBANK",
    "ICICIBANK":         "ICICIBANK",
    "AXIS":              "AXISBANK",
    "AXIS BANK":         "AXISBANK",
    "AXISBANK":          "AXISBANK",
    "SBI":               "SBIN",
    "STATE BANK":        "SBIN",
    "SBIN":              "SBIN",
    "BAJAJ FINANCE":     "BAJFINANCE",
    "BAJFINANCE":        "BAJFINANCE",
    "BAJAJ FINSERV":     "BAJAJFINSV",
    "BAJAJFINSV":        "BAJAJFINSV",
    "HUL":               "HINDUNILVR",
    "HINDUSTAN UNILEVER": "HINDUNILVR",
    "HINDUNILVR":        "HINDUNILVR",
    "HINDUSTAN LEVER":   "HINDUNILVR",
    "MARUTI":            "MARUTI",
    "MARUTI SUZUKI":     "MARUTI",
    "ITC":               "ITC",
    "NTPC":              "NTPC",
    "POWERGRID":         "POWERGRID",
    "POWER GRID":        "POWERGRID",
    "ONGC":              "ONGC",
    "OIL AND NATURAL GAS": "ONGC",
    "COAL INDIA":        "COALINDIA",
    "COALINDIA":         "COALINDIA",
    "BHARTI AIRTEL":     "BHARTIARTL",
    "AIRTEL":            "BHARTIARTL",
    "BHARTIARTL":        "BHARTIARTL",
    "TITAN":             "TITAN",
    "ADANI PORTS":       "ADANIPORTS",
    "ADANIPORTS":        "ADANIPORTS",
    "ADANI ENTERPRISES": "ADANIENT",
    "ADANIENT":          "ADANIENT",
    "ADANI GREEN":       "ADANIGREEN",
    "ADANIGREEN":        "ADANIGREEN",
    "ADANI POWER":       "ADANIPOWER",
    "TATA MOTORS":       "TATAMOTORS",
    "TATAMOTORS":        "TATAMOTORS",
    "TATA STEEL":        "TATASTEEL",
    "TATASTEEL":         "TATASTEEL",
    "TATA POWER":        "TATAPOWER",
    "TATAPOWER":         "TATAPOWER",
    "INFRA":             "INFRATEL",
    "JSPL":              "JINDALSTEL",
    "JINDAL STEEL":      "JINDALSTEL",
    "JINDALSTEL":        "JINDALSTEL",
    "HINDALCO":          "HINDALCO",
    "JSWSTEEL":          "JSWSTEEL",
    "JSW STEEL":         "JSWSTEEL",
    "ULTRATECH":         "ULTRACEMCO",
    "ULTRACEMCO":        "ULTRACEMCO",
    "ULTRATECH CEMENT":  "ULTRACEMCO",
    "GRASIM":            "GRASIM",
    "SHREECEM":          "SHREECEM",
    "SHREE CEMENT":      "SHREECEM",
    "HCLTECH":           "HCLTECH",
    "HCL TECH":          "HCLTECH",
    "HCL TECHNOLOGIES":  "HCLTECH",
    "TECH MAHINDRA":     "TECHM",
    "TECHM":             "TECHM",
    "M&M":               "M&M",
    "MAHINDRA":          "M&M",
    "MAHINDRA AND MAHINDRA": "M&M",
    "DRREDDY":           "DRREDDY",
    "DR REDDY":          "DRREDDY",
    "DR REDDY'S":        "DRREDDY",
    "CIPLA":             "CIPLA",
    "SUNPHARMA":         "SUNPHARMA",
    "SUN PHARMA":        "SUNPHARMA",
    "APOLLOHOSP":        "APOLLOHOSP",
    "APOLLO HOSPITAL":   "APOLLOHOSP",
    "DIVIS":             "DIVISLAB",
    "DIVISLAB":          "DIVISLAB",
    "DIVI'S LABS":       "DIVISLAB",
    "ASIANPAINT":        "ASIANPAINT",
    "ASIAN PAINTS":      "ASIANPAINT",
    "BERGER":            "BERGEPAINT",
    "BERGEPAINT":        "BERGEPAINT",
    "PIDILITE":          "PIDILITIND",
    "PIDILITIND":        "PIDILITIND",
    "HAVELLS":           "HAVELLS",
    "VOLTAS":            "VOLTAS",
    "SIEMENS":           "SIEMENS",
    "ABB":               "ABB",
    "LT":                "LT",
    "L&T":               "LT",
    "LARSEN":            "LT",
    "LARSEN AND TOUBRO": "LT",
    "ZOMATO":            "ZOMATO",
    "PAYTM":             "PAYTM",
    "ONE97":             "PAYTM",
    "NYKAA":             "FSN",
    "FSN":               "FSN",
    "POLICYBAZAAR":      "POLICYBZR",
    "POLICYBZR":         "POLICYBZR",
    "DELHIVERY":         "DELHIVERY",
    "IRCTC":             "IRCTC",
    "INDIANRAILWAY":     "IRCTC",
    "HAL":               "HAL",
    "BEL":               "BEL",
    "BHARAT ELECTRONICS": "BEL",
    "BHEL":              "BHEL",
    "BHARAT HEAVY":      "BHEL",
    "INFY":              "INFY",   # already correct
    "RELIANCE.NS":       "RELIANCE",
}


def resolve_ticker(user_input: str) -> tuple[str, bool]:
    """
    Resolve user input to correct NSE ticker.
    Returns (resolved_ticker, was_corrected).
    Strips .NS suffix, uppercases, checks alias map.
    """
    raw = user_input.strip().upper().replace(".NS", "").replace("-", "").strip()
    if raw in TICKER_MAP:
        resolved = TICKER_MAP[raw]
        corrected = resolved != raw
        return resolved, corrected
    return raw, False


# Popular NSE tickers for hint display
POPULAR_TICKERS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "WIPRO", "SBIN", "ITC", "MARUTI", "AXISBANK",
    "BAJFINANCE", "HCLTECH", "TECHM", "TATAMOTORS", "TATASTEEL",
    "SUNPHARMA", "DRREDDY", "CIPLA", "TITAN", "BHARTIARTL",
    "ADANIPORTS", "NTPC", "POWERGRID", "ONGC", "COALINDIA",
    "ULTRACEMCO", "LT", "GRASIM", "ASIANPAINT", "HINDUNILVR",
    "ZOMATO", "IRCTC", "HAL", "BEL", "DIVISLAB"
]
