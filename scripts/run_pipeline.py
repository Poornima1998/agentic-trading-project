from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.backtesting import VectorizedBacktester
from src.config import PROCESSED_DIR
from src.data_ingestion import MarketDataIngestion, parse_symbols
from src.decision_engine import DecisionEngine
from src.indicators import add_technical_indicators
from src.news_sentiment import fetch_news_sentiment
from src.preprocessing import clean_market_data
from src.risk_management import RiskManager
from src.utils import save_dataframe, save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AgentTrade AI pipeline.")
    parser.add_argument("--symbols", nargs="+", required=True, help="One or more asset symbols, e.g. AAPL MSFT BTC-USD")
    parser.add_argument("--period", default="1y", help="Yahoo Finance period, e.g. 6mo, 1y, 2y")
    parser.add_argument("--interval", default="1d", help="Yahoo Finance interval, e.g. 1d, 1h")
    return parser.parse_args()


def attach_symbol_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    sentiment_rows = []
    for symbol in sorted(df["symbol"].unique()):
        result = fetch_news_sentiment(symbol)
        sentiment_rows.append({
            "symbol": result.symbol,
            "sentiment_score": result.sentiment_score,
            "article_count": result.article_count,
        })
    sentiment_df = pd.DataFrame(sentiment_rows)
    return df.merge(sentiment_df, on="symbol", how="left")


def main() -> None:
    args = parse_args()
    symbols = parse_symbols(args.symbols)

    ingestion = MarketDataIngestion(symbols=symbols, period=args.period, interval=args.interval)
    raw_df = ingestion.fetch_all()
    raw_paths = ingestion.save_raw_files(raw_df)

    cleaned_df = clean_market_data(raw_df)
    featured_df = add_technical_indicators(cleaned_df)
    featured_df = attach_symbol_sentiment(featured_df)

    decision_engine = DecisionEngine()
    signal_df = decision_engine.generate_signals(featured_df)

    risk_manager = RiskManager()
    final_df = risk_manager.enrich_with_trade_levels(signal_df)

    backtester = VectorizedBacktester()
    backtest_result = backtester.run(final_df)

    processed_path = PROCESSED_DIR / f"signals_{'_'.join(symbols)}_{args.period}_{args.interval}.csv"
    save_dataframe(final_df, processed_path, index=False)
    equity_path = PROCESSED_DIR / f"equity_{'_'.join(symbols)}_{args.period}_{args.interval}.csv"
    save_dataframe(backtest_result.equity_curve, equity_path, index=False)
    metrics_path = PROCESSED_DIR / f"metrics_{'_'.join(symbols)}_{args.period}_{args.interval}.json"
    save_json(backtest_result.metrics, metrics_path)

    print("Pipeline completed successfully.")
    print(f"Saved raw files: {[str(path) for path in raw_paths]}")
    print(f"Saved processed signals: {processed_path}")
    print(f"Saved equity curve: {equity_path}")
    print(f"Saved metrics: {metrics_path}")
    print(f"Backtest metrics: {backtest_result.metrics}")


if __name__ == "__main__":
    main()
