import pandas as pd
import yfinance as yf
from app.models import StockMetrics


def fetch_nse_stock_data(symbol: str) -> StockMetrics:
  """Fetches live market data and technical indicators for an NSE stock.

  Automatically formats ticker with .NS suffix for NSE India.
  """
  clean_symbol = symbol.strip().upper().replace(".NS", "")
  nse_symbol = f"{clean_symbol}.NS"

  ticker = yf.Ticker(nse_symbol)
  df = ticker.history(period="6mo")

  if df.empty:
    raise ValueError(
        f"Could not fetch data for '{clean_symbol}'. Verify the NSE ticker."
    )

  # Current price
  current_price = round(float(df["Close"].iloc[-1]), 2)

  # ATR (14 period)
  df["H-L"] = df["High"] - df["Low"]
  df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
  df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
  df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
  df["ATR"] = df["TR"].rolling(14).mean()
  atr_14 = round(
      float(df["ATR"].iloc[-1])
      if not pd.isna(df["ATR"].iloc[-1])
      else current_price * 0.02,
      2,
  )

  # Moving Averages
  sma_20 = round(float(df["Close"].rolling(20).mean().iloc[-1]), 2)
  sma_50 = round(float(df["Close"].rolling(50).mean().iloc[-1]), 2)

  # RSI (14 period)
  delta = df["Close"].diff()
  gain = (delta.where(delta > 0, 0)).rolling(14).mean()
  loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
  rs = gain / loss
  rsi_14 = round(float((100 - (100 / (1 + rs))).iloc[-1]), 2)

  # 52 Week High/Low
  df_year = ticker.history(period="1y")
  high_52w = round(float(df_year["High"].max()), 2)
  low_52w = round(float(df_year["Low"].min()), 2)

  return StockMetrics(
      symbol=clean_symbol,
      current_price=current_price,
      atr_14=atr_14,
      sma_20=sma_20,
      sma_50=sma_50,
      rsi_14=rsi_14,
      high_52w=high_52w,
      low_52w=low_52w,
  )
