from __future__ import annotations

import numpy as np
import pandas as pd


BUY = "BUY"
SELL = "SELL"
HOLD = "HOLD"


class DecisionEngine:
    """Transparent hybrid decision engine for Buy / Sell / Hold generation."""

    def __init__(self, buy_threshold: int = 3, sell_threshold: int = -2) -> None:
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def score_row(self, row: pd.Series) -> int:
        score = 0

        sma_10 = row.get("sma_10", np.nan)
        sma_20 = row.get("sma_20", np.nan)
        if pd.notna(sma_10) and pd.notna(sma_20):
            if sma_10 > sma_20:
                score += 1
            elif sma_10 < sma_20:
                score -= 1

        macd = row.get("macd", np.nan)
        macd_signal = row.get("macd_signal", np.nan)
        if pd.notna(macd) and pd.notna(macd_signal):
            if macd > macd_signal:
                score += 1
            elif macd < macd_signal:
                score -= 1

        rsi = row.get("rsi_14", np.nan)
        if 30 <= rsi <= 65:
            score += 1
        elif rsi >= 70:
            score -= 1
        elif rsi < 30:
            score += 1

        sentiment = row.get("sentiment_score", 0.0)
        if sentiment > 0:
            score += 1
        elif sentiment < 0:
            score -= 1

        volatility = row.get("rolling_volatility_20", np.nan)
        if pd.notna(volatility) and volatility > 0.05:
            score -= 1

        return score

    def classify_score(self, score: int) -> str:
        if score >= self.buy_threshold:
            return BUY
        if score <= self.sell_threshold:
            return SELL
        return HOLD

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        signals = df.copy()
        signals["signal_score"] = signals.apply(self.score_row, axis=1)
        signals["signal"] = signals["signal_score"].apply(self.classify_score)
        return signals
