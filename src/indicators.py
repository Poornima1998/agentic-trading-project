from __future__ import annotations

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD, SMAIndicator
from ta.volatility import BollingerBands


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add common technical indicators used by the decision engine."""
    frames: list[pd.DataFrame] = []
    for symbol, group in df.groupby("symbol", sort=False):
        g = group.sort_values("date").copy()

        g["sma_10"] = SMAIndicator(close=g["close"], window=10).sma_indicator()
        g["sma_20"] = SMAIndicator(close=g["close"], window=20).sma_indicator()
        g["sma_50"] = SMAIndicator(close=g["close"], window=50).sma_indicator()
        g["ema_12"] = EMAIndicator(close=g["close"], window=12).ema_indicator()
        g["ema_26"] = EMAIndicator(close=g["close"], window=26).ema_indicator()
        g["rsi_14"] = RSIIndicator(close=g["close"], window=14).rsi()

        macd = MACD(close=g["close"], window_slow=26, window_fast=12, window_sign=9)
        g["macd"] = macd.macd()
        g["macd_signal"] = macd.macd_signal()
        g["macd_diff"] = macd.macd_diff()

        bb = BollingerBands(close=g["close"], window=20, window_dev=2)
        g["bb_high"] = bb.bollinger_hband()
        g["bb_low"] = bb.bollinger_lband()
        g["bb_mid"] = bb.bollinger_mavg()
        g["bb_width"] = bb.bollinger_wband()

        g["trend_up"] = (g["sma_10"] > g["sma_20"]) & (g["sma_20"] > g["sma_50"])
        g["trend_down"] = (g["sma_10"] < g["sma_20"]) & (g["sma_20"] < g["sma_50"])
        frames.append(g)

    return pd.concat(frames, ignore_index=True)
