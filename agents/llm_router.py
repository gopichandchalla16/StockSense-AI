"""
StockSense AI — Resilient LLM Router
Tier 1: Gemini 2.0 Flash
Tier 2: HuggingFace Mistral-7B-Instruct
Tier 3: Offline rule-based brief (always works, no API needed)
"""
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL   = "gemini-2.0-flash"
HF_MODEL_URL   = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
HF_BACKUP_URL  = "https://api-inference.huggingface.co/models/google/flan-t5-large"

# ── Key loader ─────────────────────────────────────────────────────────
def _get_keys():
    try:
        import streamlit as st
        gemini_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        hf_key     = st.secrets.get("HF_TOKEN")        or os.getenv("HF_TOKEN", "")
    except Exception:
        gemini_key = os.getenv("GOOGLE_API_KEY", "")
        hf_key     = os.getenv("HF_TOKEN", "")
    return gemini_key, hf_key

# ── Tier 1: Gemini ──────────────────────────────────────────────────────
def call_gemini(prompt: str):
    gemini_key, _ = _get_keys()
    if not gemini_key:
        return None, "Gemini key missing"
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        resp  = model.generate_content(prompt)
        text  = getattr(resp, "text", "") or ""
        if text.strip():
            return text.strip(), "Gemini"
        return None, "Gemini empty response"
    except Exception as e:
        err = str(e)
        # surface quota/auth errors clearly so they don't cause confusion
        if "429" in err or "quota" in err.lower():
            return None, "Gemini quota exceeded"
        if "403" in err or "API_KEY" in err.upper():
            return None, "Gemini invalid API key"
        return None, f"Gemini error: {err[:80]}"

# ── Tier 2: HuggingFace Mistral-7B ─────────────────────────────────────
def call_huggingface(prompt: str, url: str = HF_MODEL_URL):
    _, hf_key = _get_keys()
    headers   = {"Content-Type": "application/json"}
    if hf_key:
        headers["Authorization"] = f"Bearer {hf_key}"

    payload = {
        "inputs": f"[INST] {prompt} [/INST]",
        "parameters": {
            "max_new_tokens": 320,
            "temperature":    0.45,
            "return_full_text": False,
        },
        "options": {"wait_for_model": True},
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=40)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and data:
                text = data[0].get("generated_text", "").strip()
                if text and len(text) > 60:
                    return text, "HuggingFace"
        if r.status_code == 503:
            # Model loading — try backup
            return call_huggingface(prompt, HF_BACKUP_URL)
        return None, f"HF {r.status_code}"
    except requests.Timeout:
        return None, "HF timeout"
    except Exception as e:
        return None, f"HF error: {str(e)[:80]}"

# ── Tier 3: Offline rule-based brief ────────────────────────────────────
def offline_brief(
    ticker: str,
    pattern_data: dict,
    signal_data:  dict,
    sentiment_data: dict,
) -> str:
    price   = pattern_data.get("current_price", 0)
    ch1     = pattern_data.get("price_change_1d", 0)
    ch5     = pattern_data.get("price_change_5d", 0)
    sector  = signal_data.get("sector", "N/A")
    company = signal_data.get("company_name", ticker)
    patterns = pattern_data.get("patterns", [])
    signals  = signal_data.get("signals",  [])
    sentiment = sentiment_data.get("overall_sentiment", "NEUTRAL")
    sent_score = sentiment_data.get("sentiment_score", 50)

    bullish = sum(1 for p in patterns if "BULL" in p.get("signal", ""))
    bearish = sum(1 for p in patterns if "BEAR" in p.get("signal", ""))
    bias    = "BULLISH" if bullish > bearish else "BEARISH" if bearish > bullish else "NEUTRAL"
    bias_icon = "🟢" if bias == "BULLISH" else "🔴" if bias == "BEARISH" else "🟡"

    top_pattern = patterns[0].get("pattern", "No clear pattern") if patterns else "No clear pattern"
    top_signal  = signals[0].get("signal_type", "No trigger")     if signals  else "No trigger"
    top_conf    = int(patterns[0].get("confidence", 0.5) * 100)   if patterns else 50

    action_map = {
        "BULLISH": "📈 WATCH FOR ENTRY ON DIPS — momentum is building",
        "BEARISH": "📉 AVOID FRESH ENTRY — wait for stabilization",
        "NEUTRAL": "⏸️  HOLD & MONITOR — no clear directional signal yet",
    }
    action = action_map[bias]

    fund = signal_data.get("fundamentals", {})
    pe   = fund.get("pe_ratio", "N/A")
    hi52 = fund.get("52w_high", "N/A")
    lo52 = fund.get("52w_low",  "N/A")

    return f"""## 📊 AI Market Brief: {company} ({ticker})

**{company}** is trading at **₹{price:,.2f}**, posting a **{ch1:+.2f}% 1-day move** and **{ch5:+.2f}% over 5 days**.
Sector: **{sector}** | P/E: **{pe}** | 52W Range: ₹{lo52} – ₹{hi52}

---

## 🔍 What the Charts Say
{bias_icon} Technical bias is **{bias}** based on {len(patterns)} detected patterns.
Strongest signal: **{top_pattern}** (confidence: {top_conf}%)

## 💡 Key Opportunity / Risk
Primary trigger: **{top_signal}**
News sentiment: **{sentiment}** (Score: {sent_score}/100)

## ✅ Suggested Action
**{action}**

---
*⚙️ Generated by StockSense AI offline engine (LLM unavailable)*
*⚠️ For educational purposes only. Not SEBI-registered investment advice.*""".strip()

# ── Main entry point ─────────────────────────────────────────────────────
def generate_resilient_brief(
    prompt:        str,
    ticker:        str,
    pattern_data:  dict,
    signal_data:   dict,
    sentiment_data: dict,
) -> str:
    """Always returns a brief — never crashes. Tries Gemini → HF → offline."""
    # Tier 1 — Gemini
    text, src = call_gemini(prompt)
    if text and len(text) > 80:
        return text + "\n\n---\n*🤖 Generated by Gemini 2.0 Flash · StockSense AI*"

    gemini_fail_reason = src

    # Tier 2 — HuggingFace
    text, src = call_huggingface(prompt)
    if text and len(text) > 80:
        return text + f"\n\n---\n*🤖 Generated by HuggingFace (Gemini: {gemini_fail_reason})*"

    # Tier 3 — Offline (guaranteed)
    brief = offline_brief(ticker, pattern_data, signal_data, sentiment_data)
    return brief + f"\n\n*[Gemini: {gemini_fail_reason} | HF: {src}]*"
