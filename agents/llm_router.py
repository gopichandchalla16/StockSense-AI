"""
LLM Router — StockSense AI | NeuralForge
Tries Gemini 2.0 Flash first, falls back to HuggingFace Inference API.
Best HF model for financial analysis: mistralai/Mistral-7B-Instruct-v0.3
(free, no GPU needed, strong reasoning, instruction-tuned)
"""
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-2.0-flash"
HF_MODEL     = "mistralai/Mistral-7B-Instruct-v0.3"
HF_API_URL   = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


def _get_keys():
    try:
        import streamlit as st
        gemini_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
        hf_key     = st.secrets.get("HF_TOKEN")       or os.getenv("HF_TOKEN", "")
    except Exception:
        gemini_key = os.getenv("GOOGLE_API_KEY", "")
        hf_key     = os.getenv("HF_TOKEN", "")
    return gemini_key, hf_key


def call_llm(prompt: str, max_tokens: int = 512) -> tuple[str, str]:
    """
    Call LLM with Gemini-first, HuggingFace-fallback strategy.
    Returns (response_text, model_used).
    """
    gemini_key, hf_key = _get_keys()

    # ── Try Gemini first
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(GEMINI_MODEL)
            resp  = model.generate_content(prompt)
            return resp.text, f"Gemini {GEMINI_MODEL}"
        except Exception as gemini_err:
            gemini_error_str = str(gemini_err)
    else:
        gemini_error_str = "No GOOGLE_API_KEY set"

    # ── Fallback: HuggingFace Inference API (free, no GPU)
    # Works even without HF_TOKEN for public models (rate limited)
    headers = {"Content-Type": "application/json"}
    if hf_key:
        headers["Authorization"] = f"Bearer {hf_key}"

    # Format as Mistral instruction prompt
    hf_prompt = f"[INST] {prompt} [/INST]"
    payload = {
        "inputs": hf_prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.7,
            "return_full_text": False,
            "do_sample": True,
        }
    }
    try:
        r = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            result = r.json()
            if isinstance(result, list) and result:
                text = result[0].get("generated_text", "").strip()
                if text:
                    return text, f"HuggingFace {HF_MODEL}"
        # If Mistral is loading, try a smaller faster model
        alt_url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
        r2 = requests.post(alt_url, headers=headers,
                           json={"inputs": prompt[:1000], "parameters": {"max_new_tokens": 300}},
                           timeout=20)
        if r2.status_code == 200:
            result2 = r2.json()
            if isinstance(result2, list) and result2:
                text2 = result2[0].get("generated_text", "").strip()
                if text2:
                    return text2, "HuggingFace flan-t5-large"
    except Exception as hf_err:
        pass

    # ── Both failed — return structured fallback
    return None, "offline"


def call_llm_with_fallback(prompt: str, ticker: str, pattern_data: dict,
                           signal_data: dict, max_tokens: int = 512) -> str:
    """
    Smart fallback: if both LLMs fail, generate a rule-based brief
    from pattern_data + signal_data so the app always shows something useful.
    """
    text, model_used = call_llm(prompt, max_tokens)

    if text and len(text.strip()) > 50:
        return f"{text}\n\n---\n*Analysis by {model_used}*"

    # ── Pure rule-based fallback (no LLM needed)
    price       = pattern_data.get("current_price", 0)
    change_1d   = pattern_data.get("price_change_1d", 0)
    change_5d   = pattern_data.get("price_change_5d", 0)
    patterns    = pattern_data.get("patterns", [])
    signals     = signal_data.get("signals", [])
    sector      = signal_data.get("sector", "N/A")
    fund        = signal_data.get("fundamentals", {})

    bullish = sum(1 for p in patterns if "BULL" in p.get("signal",""))
    bearish = sum(1 for p in patterns if "BEAR" in p.get("signal",""))
    overall = "BULLISH" if bullish > bearish else "BEARISH" if bearish > bullish else "NEUTRAL"
    action  = "CONSIDER BUYING on dips" if overall=="BULLISH" else \
               "CONSIDER BOOKING PROFITS" if overall=="BEARISH" else \
               "HOLD and WATCH for breakout"

    pattern_lines = "\n".join([
        f"- {p['pattern']} ({p['signal']}, {int(p.get('confidence',0.5)*100)}% confidence)"
        for p in patterns
    ]) or "- No strong pattern detected currently"

    signal_lines = "\n".join([
        f"- {s['signal_type']} [{s['strength']}]: {s['message']}"
        for s in signals
    ]) or "- No opportunity signals found"

    pe = fund.get('pe_ratio', 'N/A')
    wh = fund.get('52w_high', 'N/A')
    wl = fund.get('52w_low', 'N/A')

    return f"""## 📊 Market Brief: {ticker}

**{ticker}** is trading at ₹{price:,.2f}, with a **{change_1d:+.2f}% move today** and **{change_5d:+.2f}% over 5 days**.
Sector: **{sector}** | Overall Technical Bias: **{overall}**

## 🔍 What the Charts Say
{pattern_lines}

## 📡 Opportunity Signals
{signal_lines}

## 📊 Key Fundamentals
- P/E Ratio: **{pe}** | 52W High: **₹{wh}** | 52W Low: **₹{wl}**

## ✅ Suggested Action
**{action}** — based on {len(patterns)} technical pattern(s) detected.

## ⚠️ Disclaimer
Rule-based analysis (AI LLM temporarily unavailable). 
Not SEBI-registered advice. Always do your own research.
*StockSense AI | NeuralForge | ET GenAI Hackathon 2026*
"""
