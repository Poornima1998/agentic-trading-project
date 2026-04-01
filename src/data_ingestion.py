from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import yfinance as yf

from src.config import RAW_DIR
from src.utils import save_dataframe


@dataclass
class MarketDataIngestion:
    symbols: list[str]
    period: str = "1y"
    interval: str = "1d"

    def fetch_symbol(self, symbol: str) -> pd.DataFrame:
        """Download a single symbol from Yahoo Finance and normalize columns."""
        df = yf.download(
            tickers=symbol,
            period=self.period,
            interval=self.interval,
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if df.empty:
            raise ValueError(f"No data returned for symbol: {symbol}")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df = df.reset_index()
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
        rename_map = {
            "adj_close": "adj_close",
            "date": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }
        df = df.rename(columns=rename_map)
        df["symbol"] = symbol
        return df

    def fetch_all(self) -> pd.DataFrame:
        """Download all requested symbols and concatenate them."""
        frames = [self.fetch_symbol(symbol) for symbol in self.symbols]
        return pd.concat(frames, ignore_index=True)

    def save_raw_files(self, df: pd.DataFrame) -> list[Path]:
        """Save one raw CSV per symbol."""
        saved: list[Path] = []
        for symbol, group in df.groupby("symbol"):
            path = RAW_DIR / f"{symbol.replace('/', '_')}_{self.period}_{self.interval}.csv"
            save_dataframe(group, path, index=False)
            saved.append(path)
        return saved


def parse_symbols(symbols: Iterable[str]) -> list[str]:
    """Normalize input symbols into a non-empty list."""
    cleaned = [symbol.strip().upper() for symbol in symbols if str(symbol).strip()]
    if not cleaned:
        raise ValueError("At least one symbol must be provided.")
    return cleaned
