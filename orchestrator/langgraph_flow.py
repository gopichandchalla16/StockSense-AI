"""
LangGraph Multi-Agent Orchestrator — StockSense AI | NeuralForge
Coordinates PatternDetector → SignalFinder → Sentiment → Explanation pipeline
ET GenAI Hackathon 2026 | PS #6
"""
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from agents.pattern_agent import detect_patterns
from agents.signal_agent import get_opportunity_signals
from agents.explanation_agent import generate_market_explanation
from agents.news_sentiment_agent import analyze_news_sentiment


class AgentState(TypedDict):
    """Shared state passed between all agents in the LangGraph pipeline."""
    ticker: str
    pattern_data: Optional[Dict[str, Any]]
    signal_data: Optional[Dict[str, Any]]
    sentiment_data: Optional[Dict[str, Any]]
    explanation: Optional[str]
    error: Optional[str]
    step_log: List[str]


def pattern_detector_node(state: AgentState) -> AgentState:
    """Node 1: Fetch NSE OHLCV data and detect chart patterns using pandas-ta."""
    state["step_log"].append(
        f"🔍 PatternDetectorAgent: Fetching NSE data for {state['ticker']}..."
    )
    try:
        result = detect_patterns(state["ticker"])
        state["pattern_data"] = result
        patterns = result.get("patterns", [])
        state["step_log"].append(
            f"✅ PatternDetectorAgent: Found {len(patterns)} pattern(s) | "
            f"Price ₹{result.get('current_price', 'N/A')} | "
            f"1D Change: {result.get('price_change_1d', 0)}%"
        )
    except Exception as e:
        state["error"] = str(e)
        state["step_log"].append(f"❌ PatternDetectorAgent FAILED: {str(e)}")
    return state


def signal_finder_node(state: AgentState) -> AgentState:
    """Node 2: Scan NSE fundamentals and bulk deals for opportunity signals."""
    state["step_log"].append(
        f"📡 SignalFinderAgent: Scanning opportunity signals for {state['ticker']}..."
    )
    try:
        result = get_opportunity_signals(state["ticker"])
        state["signal_data"] = result
        signals = result.get("signals", [])
        state["step_log"].append(
            f"✅ SignalFinderAgent: Found {len(signals)} signal(s) | "
            f"Company: {result.get('company_name', 'N/A')} | "
            f"Sector: {result.get('sector', 'N/A')}"
        )
    except Exception as e:
        state["step_log"].append(f"⚠️ SignalFinderAgent warning: {str(e)}")
        state["signal_data"] = {
            "signals": [],
            "fundamentals": {},
            "company_name": state["ticker"],
            "sector": "N/A"
        }
    return state


def sentiment_node(state: AgentState) -> AgentState:
    """Node 3: Fetch news via yfinance and analyze sentiment using Gemini."""
    state["step_log"].append(
        f"📰 NewsSentimentAgent: Analyzing news for {state['ticker']}..."
    )
    try:
        result = analyze_news_sentiment(state["ticker"])
        state["sentiment_data"] = result
        state["step_log"].append(
            f"✅ NewsSentimentAgent: {result.get('overall_sentiment', 'NEUTRAL')} "
            f"(Score: {result.get('sentiment_score', 50)}/100) | "
            f"{result.get('news_count', 0)} articles analyzed"
        )
    except Exception as e:
        state["step_log"].append(f"⚠️ NewsSentimentAgent warning: {str(e)}")
        state["sentiment_data"] = {
            "overall_sentiment": "NEUTRAL",
            "sentiment_score": 50,
            "key_themes": [],
            "analysis": "Sentiment unavailable.",
            "raw_news": [],
            "news_count": 0
        }
    return state


def explanation_node(state: AgentState) -> AgentState:
    """Node 4: Generate plain-English AI market brief using Gemini 1.5 Flash."""
    state["step_log"].append(
        "🧠 ExplanationAgent: Generating AI market brief with Gemini 1.5 Flash..."
    )
    try:
        explanation = generate_market_explanation(
            state["pattern_data"] or {},
            state["signal_data"] or {},
            state["sentiment_data"]
        )
        state["explanation"] = explanation
        state["step_log"].append(
            "✅ ExplanationAgent: Market brief generated successfully"
        )
    except Exception as e:
        state["explanation"] = (
            f"## ⚠️ Analysis Unavailable\nError: {str(e)}\n\n"
            "Please check your GOOGLE_API_KEY."
        )
        state["step_log"].append(f"⚠️ ExplanationAgent warning: {str(e)}")
    return state


def should_continue(state: AgentState) -> str:
    """Conditional router: stop pipeline if critical data fetch failed completely."""
    if state.get("error") and not state.get("pattern_data"):
        state["step_log"].append(
            "🛑 Orchestrator: Critical failure in PatternDetector — ending pipeline"
        )
        return "end"
    return "continue"


def build_graph() -> StateGraph:
    """Build and compile the complete LangGraph multi-agent StateGraph."""
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("pattern_detector", pattern_detector_node)
    workflow.add_node("signal_finder", signal_finder_node)
    workflow.add_node("sentiment_analyzer", sentiment_node)
    workflow.add_node("explanation", explanation_node)

    # Entry point
    workflow.set_entry_point("pattern_detector")

    # Conditional routing after pattern detection
    workflow.add_conditional_edges(
        "pattern_detector",
        should_continue,
        {"continue": "signal_finder", "end": END}
    )

    # Linear pipeline
    workflow.add_edge("signal_finder", "sentiment_analyzer")
    workflow.add_edge("sentiment_analyzer", "explanation")
    workflow.add_edge("explanation", END)

    return workflow.compile()


def analyze_stock(ticker: str) -> AgentState:
    """
    Main entry point: run full 4-agent LangGraph pipeline for any NSE ticker.
    Returns complete AgentState with all outputs and step_log audit trail.
    """
    graph = build_graph()
    initial_state = AgentState(
        ticker=ticker.strip().upper().replace(".NS", ""),
        pattern_data=None,
        signal_data=None,
        sentiment_data=None,
        explanation=None,
        error=None,
        step_log=[]
    )
    return graph.invoke(initial_state)


if __name__ == "__main__":
    print("🚀 StockSense AI — LangGraph Multi-Agent Pipeline")
    print("Running full pipeline for WIPRO...\n")
    result = analyze_stock("WIPRO")
    print("=== AGENT AUDIT TRAIL ===")
    for log in result["step_log"]:
        print(log)
    print("\n=== AI MARKET BRIEF ===")
    print(result.get("explanation", "No explanation generated"))
