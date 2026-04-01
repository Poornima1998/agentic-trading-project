from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def save_dataframe(df: pd.DataFrame, path: str | Path, index: bool = False) -> Path:
    """Persist a DataFrame to CSV and ensure parent directories exist."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    return path


def save_json(payload: dict[str, Any], path: str | Path) -> Path:
    """Persist a JSON-serializable object to disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def annualized_sharpe(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Calculate annualized Sharpe ratio from periodic returns."""
    cleaned = returns.dropna()
    if cleaned.empty or cleaned.std() == 0:
        return 0.0
    return (cleaned.mean() / cleaned.std()) * (periods_per_year ** 0.5)


def max_drawdown(equity_curve: pd.Series) -> float:
    """Calculate maximum drawdown from an equity curve."""
    running_max = equity_curve.cummax()
    drawdown = (equity_curve / running_max) - 1.0
    return float(drawdown.min()) if not drawdown.empty else 0.0
