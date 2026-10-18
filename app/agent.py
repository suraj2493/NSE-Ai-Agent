import os
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

from app.models import StockMetrics, TradingRecommendation
from app.tools import fetch_nse_stock_data

# Uses Google Gemini (Free API token tier)
gemini_key = os.getenv("GEMINI_API_KEY")
model = GeminiModel("gemini-1.5-flash", api_key=gemini_key)

stock_agent = Agent(
    model,
    result_type=TradingRecommendation,
    system_prompt="""
    You are an expert Quantitative Indian Stock Market Technical Analyst & Risk Manager.
    Your goal is to evaluate real-time technical metrics for NSE stocks and generate 
    precise, mathematically sound Buy, Stop-Loss, and Target recommendations in Indian Rupees (₹).

    RULES FOR CALCULATIONS:
    1. Stop-Loss: MUST be placed 1.5x to 2x ATR below entry price or key moving average support (SMA 20/50).
    2. Target 1: Minimum Risk-Reward ratio of 1:1.5 from entry.
    3. Target 2: Minimum Risk-Reward ratio of 1:2.5 or key 52-week resistance zones.
    4. Buy Range: Define a reasonable zone around Current Market Price (CMP) or pullback zone near SMA 20.
    5. Always state values in INR (₹).
""",
)


def run_stock_analysis(symbol: str) -> TradingRecommendation:
  # 1. Tool Call: Deterministic Data Fetching
  metrics: StockMetrics = fetch_nse_stock_data(symbol)

  # 2. Construct Prompt with Ground Truth Data to prevent LLM hallucinations
  prompt = f"""
    Analyze the following NSE Stock Data and produce a structured recommendation:
    - Symbol: {metrics.symbol}
    - Current Market Price (CMP): ₹{metrics.current_price}
    - 14-day ATR (Volatility): ₹{metrics.atr_14}
    - 20-day SMA: ₹{metrics.sma_20}
    - 50-day SMA: ₹{metrics.sma_50}
    - 14-day RSI: {metrics.rsi_14}
    - 52-Week High: ₹{metrics.high_52w}
    - 52-Week Low: ₹{metrics.low_52w}

    Calculate exact Entry Zone, Stop-Loss, Target 1, Target 2, Risk-Reward Ratio, and Confidence Score.
    """

  # 3. Agent Execution Loop
  result = stock_agent.run_sync(prompt)
  return result.data
