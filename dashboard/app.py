from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

st.set_page_config(page_title="AgentTrade Dashboard", layout="wide")
st.title("AgentTrade AI Dashboard")
st.caption("Buy / Sell / Hold monitoring for coursework demonstration")

csv_files = sorted(PROCESSED_DIR.glob("signals_*.csv"))
if not csv_files:
    st.warning("No processed signal files found. Run scripts/run_pipeline.py first.")
    st.stop()

selected_file = st.selectbox("Select a processed signal file", csv_files, format_func=lambda p: p.name)
df = pd.read_csv(selected_file)
df["date"] = pd.to_datetime(df["date"])

symbols = sorted(df["symbol"].dropna().unique())
selected_symbol = st.selectbox("Select symbol", symbols)
view_df = df[df["symbol"] == selected_symbol].copy()

col1, col2, col3 = st.columns(3)
with col1:
    latest_price = float(view_df["close"].iloc[-1]) if not view_df.empty else 0.0
    st.metric("Latest Close", f"{latest_price:,.2f}")
with col2:
    latest_signal = view_df["signal"].iloc[-1] if not view_df.empty else "N/A"
    st.metric("Latest Signal", latest_signal)
with col3:
    latest_score = float(view_df["signal_score"].iloc[-1]) if not view_df.empty else 0.0
    st.metric("Signal Score", f"{latest_score:.0f}")

price_fig = px.line(view_df, x="date", y=["close", "sma_10", "sma_20", "sma_50"], title=f"Price and Moving Averages: {selected_symbol}")
st.plotly_chart(price_fig, use_container_width=True)

indicator_fig = px.line(view_df, x="date", y=["rsi_14", "macd", "macd_signal"], title=f"Indicators: {selected_symbol}")
st.plotly_chart(indicator_fig, use_container_width=True)

signal_counts = view_df["signal"].value_counts().rename_axis("signal").reset_index(name="count")
signal_fig = px.bar(signal_counts, x="signal", y="count", title="Signal Distribution")
st.plotly_chart(signal_fig, use_container_width=True)

st.subheader("Latest Records")
st.dataframe(view_df.tail(20), use_container_width=True)
