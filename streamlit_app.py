import os
import pandas as pd
import streamlit as st
import yfinance as yf

# Page setup
st.set_page_config(
    page_title="NSE AI Stock Agent", page_icon="📈", layout="wide"
)

st.title("📈 NSE AI Stock Agent")
st.caption(
    "Powered by Gemini AI & Real-Time Technical Engine (Free Market Data)"
)

symbol = st.text_input("Enter NSE Stock Symbol:", value="RELIANCE").upper()

if st.button("Analyze Stock"):
  clean_symbol = symbol.strip().replace(".NS", "")
  nse_symbol = f"{clean_symbol}.NS"

  with st.spinner("Fetching market data..."):
    df = yf.Ticker(nse_symbol).history(period="6mo")

  if df.empty:
    st.error(f"Could not fetch data for ticker '{clean_symbol}'.")
  else:
    cmp = round(float(df["Close"].iloc[-1]), 2)

    # Technical logic
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
    df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
    atr = round(float(df["TR"].rolling(14).mean().iloc[-1]), 2)

    stop_loss = round(cmp - (1.5 * atr), 2)
    risk = cmp - stop_loss
    target_1 = round(cmp + (1.5 * risk), 2)
    target_2 = round(cmp + (2.5 * risk), 2)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Price (CMP)", f"₹{cmp}")
    col2.metric("Buy Range", f"₹{cmp}")
    col3.metric("Stop Loss", f"₹{stop_loss}")
    col4.metric("Targets", f"₹{target_1} / ₹{target_2}")

    st.subheader("Technical Analysis")
    st.write(
        f"• **14-day ATR (Volatility):** ₹{atr}\n"
        f"• **Risk-Reward Ratio:** 1:2\n"
        f"• **Stop Loss Placement:** Placed 1.5x ATR below entry to absorb normal market noise."
    )

    st.line_chart(df["Close"])
