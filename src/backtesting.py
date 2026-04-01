from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.utils import annualized_sharpe, max_drawdown


@dataclass
class BacktestResult:
    metrics: dict[str, float]
    equity_curve: pd.DataFrame


class VectorizedBacktester:
    """A simple signal-following backtester for coursework demonstration."""

    def __init__(self, initial_capital: float = 10_000.0, transaction_cost: float = 0.001) -> None:
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost

    def run(self, df: pd.DataFrame) -> BacktestResult:
        frames: list[pd.DataFrame] = []
        summary_returns: list[float] = []

        for symbol, group in df.groupby("symbol", sort=False):
            g = group.sort_values("date").copy()
            g["asset_return"] = g["close"].pct_change().fillna(0.0)
            g["position"] = g["signal"].map({"BUY": 1, "SELL": -1, "HOLD": 0}).fillna(0)
            g["shifted_position"] = g["position"].shift(1).fillna(0)
            g["trade_flag"] = (g["shifted_position"].diff().abs().fillna(0) > 0).astype(int)
            g["strategy_return"] = (
                g["shifted_position"] * g["asset_return"]
                - g["trade_flag"] * self.transaction_cost
            )
            g["equity"] = self.initial_capital * (1 + g["strategy_return"]).cumprod()
            frames.append(g)
            summary_returns.append(g["strategy_return"].mean())

        equity_curve = pd.concat(frames, ignore_index=True)

        aggregated = equity_curve.groupby("date", as_index=False).agg(
            strategy_return=("strategy_return", "mean")
        )
        aggregated["portfolio_equity"] = self.initial_capital * (1 + aggregated["strategy_return"]).cumprod()

        total_return = (aggregated["portfolio_equity"].iloc[-1] / self.initial_capital) - 1 if not aggregated.empty else 0.0
        sharpe = annualized_sharpe(aggregated["strategy_return"] if not aggregated.empty else pd.Series(dtype=float))
        drawdown = max_drawdown(aggregated["portfolio_equity"] if not aggregated.empty else pd.Series(dtype=float))
        win_rate = float((aggregated["strategy_return"] > 0).mean()) if not aggregated.empty else 0.0

        metrics = {
            "initial_capital": self.initial_capital,
            "total_return": float(total_return),
            "annualized_sharpe": float(sharpe),
            "max_drawdown": float(drawdown),
            "win_rate": float(win_rate),
            "avg_period_return": float(sum(summary_returns) / len(summary_returns)) if summary_returns else 0.0,
        }
        return BacktestResult(metrics=metrics, equity_curve=aggregated)
