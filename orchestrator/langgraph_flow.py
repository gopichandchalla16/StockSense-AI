"""
LangGraph Multi-Agent Orchestrator — StockSense AI | NeuralForge
Coordinates PatternDetector → SignalFinder → Sentiment → Explanation pipeline
ET GenAI Hackathon 2026 | PS #6
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from agents.pattern_agent import detect_patterns
from agents.signal_agent import get_opportunity_signals
from agents.explanation_agent import generate_market_explanation
from agents.news_sentiment_agent import analyze_news_sentiment
from utils.ticker_resolver import resolve_ticker


class AgentState(TypedDict):
    ticker: str
    pattern_data: Optional[Dict[str, Any]]
    signal_data: Optional[Dict[str, Any]]
    sentiment_data: Optional[Dict[str, Any]]
    explanation: Optional[str]
    error: Optional[str]
    step_log: List[str]
    ticker_corrected: Optional[bool]
    original_input: Optional[str]


def pattern_detector_node(state: AgentState) -> AgentState:
    state["step_log"].append(f"🔍 PatternDetectorAgent: Fetching NSE data for {state['ticker']}...")
    try:
        result = detect_patterns(state["ticker"])
        state["pattern_data"] = result
        price = result.get("current_price", 0)
        if price == 0:
            state["step_log"].append(
                f"⚠️ PatternDetectorAgent: Price = ₹0 — ticker '{state['ticker']}' may be invalid. "
                f"Use exact NSE symbol (e.g. INFY not INFOSYS)"
            )
        else:
            state["step_log"].append(
                f"✅ PatternDetectorAgent: Found {len(result.get('patterns',[]))} pattern(s) | "
                f"Price ₹{price:,.2f} | 1D: {result.get('price_change_1d',0)}%"
            )
    except Exception as e:
        state["error"] = str(e)
        state["step_log"].append(f"❌ PatternDetectorAgent FAILED: {str(e)}")
    return state


def signal_finder_node(state: AgentState) -> AgentState:
    state["step_log"].append(f"📡 SignalFinderAgent: Scanning signals for {state['ticker']}...")
    try:
        result = get_opportunity_signals(state["ticker"])
        state["signal_data"] = result
        state["step_log"].append(
            f"✅ SignalFinderAgent: {len(result.get('signals',[]))} signal(s) | "
            f"{result.get('company_name','N/A')} | Sector: {result.get('sector','N/A')}"
        )
    except Exception as e:
        state["step_log"].append(f"⚠️ SignalFinderAgent: {str(e)}")
        state["signal_data"] = {
            "signals": [], "fundamentals": {},
            "company_name": state["ticker"], "sector": "N/A"
        }
    return state


def sentiment_node(state: AgentState) -> AgentState:
    state["step_log"].append(f"📰 NewsSentimentAgent: Analyzing news for {state['ticker']}...")
    try:
        result = analyze_news_sentiment(state["ticker"])
        state["sentiment_data"] = result
        state["step_log"].append(
            f"✅ NewsSentimentAgent: {result.get('overall_sentiment','NEUTRAL')} "
            f"({result.get('sentiment_score',50)}/100) | {result.get('news_count',0)} articles"
        )
    except Exception as e:
        state["step_log"].append(f"⚠️ NewsSentimentAgent: {str(e)}")
        state["sentiment_data"] = {
            "overall_sentiment": "NEUTRAL", "sentiment_score": 50,
            "key_themes": [], "analysis": "Unavailable.",
            "raw_news": [], "news_count": 0
        }
    return state


def explanation_node(state: AgentState) -> AgentState:
    state["step_log"].append("🧠 ExplanationAgent: Generating AI market brief...")
    try:
        explanation = generate_market_explanation(
            state["pattern_data"] or {},
            state["signal_data"] or {},
            state["sentiment_data"]
        )
        state["explanation"] = explanation
        state["step_log"].append("✅ ExplanationAgent: Market brief generated")
    except Exception as e:
        state["explanation"] = f"## ⚠️ Brief Unavailable\n{str(e)}"
        state["step_log"].append(f"⚠️ ExplanationAgent: {str(e)}")
    return state


def should_continue(state: AgentState) -> str:
    pd = state.get("pattern_data") or {}
    if state.get("error") and not pd:
        return "end"
    if pd.get("current_price", 0) == 0 and pd.get("error"):
        return "end"
    return "continue"


def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("pattern_detector",  pattern_detector_node)
    workflow.add_node("signal_finder",      signal_finder_node)
    workflow.add_node("sentiment_analyzer", sentiment_node)
    workflow.add_node("explanation",        explanation_node)
    workflow.set_entry_point("pattern_detector")
    workflow.add_conditional_edges(
        "pattern_detector", should_continue,
        {"continue": "signal_finder", "end": END}
    )
    workflow.add_edge("signal_finder",      "sentiment_analyzer")
    workflow.add_edge("sentiment_analyzer", "explanation")
    workflow.add_edge("explanation",        END)
    return workflow.compile()


def analyze_stock(ticker: str) -> AgentState:
    """
    Main entry: resolve ticker alias then run full 4-agent LangGraph pipeline.
    e.g. INFOSYS → INFY, HDFC → HDFCBANK automatically.
    """
    resolved, was_corrected = resolve_ticker(ticker)
    graph = build_graph()
    state = AgentState(
        ticker=resolved,
        original_input=ticker.strip().upper(),
        ticker_corrected=was_corrected,
        pattern_data=None, signal_data=None,
        sentiment_data=None, explanation=None,
        error=None, step_log=[]
    )
    if was_corrected:
        state["step_log"].append(
            f"🔄 Ticker resolved: '{ticker.upper()}' → '{resolved}' (NSE symbol auto-corrected)"
        )
    return graph.invoke(state)


if __name__ == "__main__":
    for t in ["INFOSYS", "HDFC", "RELIANCE", "SBI", "L&T"]:
        r = analyze_stock(t)
        print(f"{t} → {r['ticker']} | Price: ₹{(r.get('pattern_data') or {}).get('current_price', 0)}")
