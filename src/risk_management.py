from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class RiskConfig:
    initial_capital: float = 10_000.0
    risk_per_trade: float = 0.02
    stop_loss_pct: float = 0.03
    take_profit_pct: float = 0.06
    max_position_pct: float = 0.25


class RiskManager:
    def __init__(self, config: RiskConfig | None = None) -> None:
        self.config = config or RiskConfig()

    def position_size(self, price: float, capital: float | None = None) -> int:
        """Calculate whole-unit position sizing using max risk and max allocation."""
        available_capital = capital if capital is not None else self.config.initial_capital
        capital_at_risk = available_capital * self.config.risk_per_trade
        max_allocation = available_capital * self.config.max_position_pct

        if price <= 0:
            return 0

        qty_by_risk = capital_at_risk / (price * self.config.stop_loss_pct)
        qty_by_allocation = max_allocation / price
        quantity = int(max(0, min(qty_by_risk, qty_by_allocation)))
        return quantity

    def enrich_with_trade_levels(self, df: pd.DataFrame) -> pd.DataFrame:
        enriched = df.copy()
        enriched["position_qty"] = enriched["close"].apply(self.position_size)
        enriched["stop_loss_price"] = enriched["close"] * (1 - self.config.stop_loss_pct)
        enriched["take_profit_price"] = enriched["close"] * (1 + self.config.take_profit_pct)
        return enriched
