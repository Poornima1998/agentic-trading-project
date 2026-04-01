from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = ["date", "open", "high", "low", "close", "volume", "symbol"]


def validate_columns(df: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def clean_market_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean market data for downstream analytics."""
    validate_columns(df)
    cleaned = df.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned = cleaned.dropna(subset=["date", "open", "high", "low", "close"])
    cleaned = cleaned.sort_values(["symbol", "date"]).drop_duplicates(subset=["symbol", "date"])

    numeric_columns = ["open", "high", "low", "close", "volume"]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=["open", "high", "low", "close"])
    cleaned["volume"] = cleaned["volume"].fillna(0)

    # Basic anomaly handling: remove impossible negative prices/volumes.
    cleaned = cleaned[(cleaned[["open", "high", "low", "close", "volume"]] >= 0).all(axis=1)]
    cleaned["daily_return"] = cleaned.groupby("symbol")["close"].pct_change()
    cleaned["rolling_volatility_20"] = (
        cleaned.groupby("symbol")["daily_return"].transform(lambda s: s.rolling(20).std())
    )
    return cleaned.reset_index(drop=True)
