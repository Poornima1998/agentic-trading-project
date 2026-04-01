from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from src.config import settings


@dataclass
class NewsSentimentResult:
    symbol: str
    sentiment_score: float
    article_count: int
    headlines: list[str]


POSITIVE_TERMS = {"beat", "growth", "gain", "surge", "bullish", "record", "profit", "expands"}
NEGATIVE_TERMS = {"drop", "fall", "loss", "lawsuit", "risk", "bearish", "cuts", "decline"}


def simple_headline_sentiment(headlines: list[str]) -> float:
    """Very lightweight keyword-based sentiment scoring for coursework usage."""
    if not headlines:
        return 0.0

    score = 0
    for headline in headlines:
        tokens = {token.strip(".,:;!?()[]{}\"'").lower() for token in headline.split()}
        score += len(tokens & POSITIVE_TERMS)
        score -= len(tokens & NEGATIVE_TERMS)
    return score / len(headlines)


def fetch_news_sentiment(symbol: str) -> NewsSentimentResult:
    """Fetch recent headlines from NewsAPI if configured, otherwise return neutral sentiment."""
    if not settings.newsapi_key:
        return NewsSentimentResult(symbol=symbol, sentiment_score=0.0, article_count=0, headlines=[])

    endpoint = "https://newsapi.org/v2/everything"
    from_date = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
    params: dict[str, Any] = {
        "q": symbol,
        "from": from_date,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 10,
        "apiKey": settings.newsapi_key,
    }

    response = requests.get(endpoint, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    articles = payload.get("articles", [])
    headlines = [article.get("title", "") for article in articles if article.get("title")]
    score = simple_headline_sentiment(headlines)
    return NewsSentimentResult(
        symbol=symbol,
        sentiment_score=score,
        article_count=len(headlines),
        headlines=headlines,
    )
