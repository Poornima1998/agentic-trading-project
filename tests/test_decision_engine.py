import pandas as pd

from src.decision_engine import BUY, HOLD, SELL, DecisionEngine


def test_decision_engine_buy_signal() -> None:
    df = pd.DataFrame([
        {
            "sma_10": 110,
            "sma_20": 100,
            "macd": 2.0,
            "macd_signal": 1.0,
            "rsi_14": 55,
            "sentiment_score": 0.3,
            "rolling_volatility_20": 0.02,
        }
    ])
    engine = DecisionEngine()
    out = engine.generate_signals(df)
    assert out.loc[0, "signal"] == BUY


def test_decision_engine_sell_signal() -> None:
    df = pd.DataFrame([
        {
            "sma_10": 90,
            "sma_20": 100,
            "macd": -2.0,
            "macd_signal": -1.0,
            "rsi_14": 75,
            "sentiment_score": -0.4,
            "rolling_volatility_20": 0.07,
        }
    ])
    engine = DecisionEngine()
    out = engine.generate_signals(df)
    assert out.loc[0, "signal"] == SELL


def test_decision_engine_hold_signal() -> None:
    df = pd.DataFrame([
        {
            "sma_10": 100,
            "sma_20": 100,
            "macd": 0.1,
            "macd_signal": 0.1,
            "rsi_14": 68,
            "sentiment_score": 0.0,
            "rolling_volatility_20": 0.02,
        }
    ])
    engine = DecisionEngine()
    out = engine.generate_signals(df)
    assert out.loc[0, "signal"] == HOLD
