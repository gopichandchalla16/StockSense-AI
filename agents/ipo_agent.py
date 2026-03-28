"""
IPOIntelligenceAgent — StockSense AI
Team NeuralForge | ET GenAI Hackathon 2026

Fetches upcoming IPO data from NSE India and generates AI-powered
buy/avoid verdicts using Gemini 1.5 Flash.
"""

import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

FALLBACK_IPOS = [
    {
        "company": "Sample Infrastructure Ltd",
        "open_date": "01 Apr 2026",
        "close_date": "03 Apr 2026",
        "price_band": "₹120–₹130",
        "lot_size": 115,
        "issue_size": "₹650 Cr",
        "gmp": "+₹18",
        "category": "Mainboard"
    },
    {
        "company": "TechVentures SME Ltd",
        "open_date": "02 Apr 2026",
        "close_date": "04 Apr 2026",
        "price_band": "₹200–₹210",
        "lot_size": 70,
        "issue_size": "₹280 Cr",
        "gmp": "+₹35",
        "category": "SME"
    }
]


def _configure_gemini():
    """Configure Gemini API key from environment or Streamlit secrets."""
    try:
        import streamlit as st
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    except Exception:
        api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)


def fetch_ipo_data() -> List[Dict]:
    """Fetch current IPO data from NSE India public endpoint."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nseindia.com/",
            "Accept": "application/json"
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=8)
        url = "https://www.nseindia.com/api/ipo-current-allotment"
        resp = session.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return data[:6]
    except Exception as e:
        print(f"[IPOAgent] NSE IPO API error: {e}")
    return FALLBACK_IPOS


def analyze_ipo(ipo: Dict) -> str:
    """Use Gemini to generate a concise IPO investment verdict."""
    _configure_gemini()
    prompt = f"""You are an IPO analyst for Indian retail investors on NSE/BSE.
Analyze this IPO and give a clear, concise recommendation.

IPO Details:
- Company: {ipo.get('company', 'N/A')}
- Price Band: {ipo.get('price_band', 'N/A')}
- Lot Size: {ipo.get('lot_size', 'N/A')} shares
- Issue Size: {ipo.get('issue_size', 'N/A')}
- GMP (Grey Market Premium): {ipo.get('gmp', 'N/A')}
- Category: {ipo.get('category', 'Mainboard')}

Reply in EXACTLY this format (max 80 words):
VERDICT: [STRONG SUBSCRIBE / SUBSCRIBE / NEUTRAL / AVOID]
REASON: [1 key reason — be specific]
RISK: [1 key risk]
⚠️ Not SEBI-registered advice. Do your own research before investing."""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        return f"AI verdict unavailable. GMP: {ipo.get('gmp', 'N/A')}\n⚠️ Not investment advice."


def get_ipo_intelligence() -> Dict[str, Any]:
    """Main function: fetch all IPOs and generate AI verdict for each."""
    ipos = fetch_ipo_data()
    analyzed = []
    for ipo in ipos[:5]:
        verdict = analyze_ipo(ipo)
        analyzed.append({**ipo, "ai_verdict": verdict})
    return {"ipos": analyzed, "count": len(analyzed)}


if __name__ == "__main__":
    print("Testing IPOIntelligenceAgent...")
    result = get_ipo_intelligence()
    print(f"IPOs found: {result['count']}")
    for ipo in result['ipos']:
        print(f"\n{ipo.get('company')}:")
        print(ipo.get('ai_verdict', 'No verdict'))
