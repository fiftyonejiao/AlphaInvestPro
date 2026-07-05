"""Market data access: quotes, price history, and news through QVeris.

All QVeris responses are normalized into internal schemas before reaching
analysis agents or the UI. When QVeris is not configured, the service
falls back to explicit MOCK DATA.
"""

import logging
from typing import Optional

from ..schemas.qveris import (
    DataPointMeta,
    MarketDataBundle,
    NewsItem,
    NormalizedNews,
    NormalizedPriceHistory,
    NormalizedQuote,
    PricePoint,
    QverisStatus,
)
from . import mock_data
from .fundamentals_service import FundamentalsService
from .qveris_client import QverisApiError, QverisClient, QverisNotConfiguredError

logger = logging.getLogger(__name__)


class MarketDataService:
    def __init__(self, client: Optional[QverisClient] = None):
        self.client = client or QverisClient()
        self.fundamentals = FundamentalsService(self.client)

    def status(self) -> QverisStatus:
        return QverisStatus(
            configured=self.client.is_configured,
            base_url=self.client.base_url,
            session_id=self.client.session_id,
            mode="live" if self.client.is_configured else "mock",
        )

    def _normalize_quote(self, symbol: str, raw: dict, capability_id: Optional[str]) -> NormalizedQuote:
        data = raw.get("data", raw)
        return NormalizedQuote(
            symbol=symbol,
            price=float(data.get("price") or data.get("last") or 0.0),
            change_percent=data.get("change_percent"),
            volume=data.get("volume"),
            market_cap=data.get("market_cap"),
            meta=DataPointMeta(
                provider=raw.get("provider", "qveris"),
                capability_id=capability_id,
                source_timestamp=data.get("timestamp") or raw.get("timestamp"),
                currency=data.get("currency", "USD"),
                symbol=symbol,
                market=data.get("market", "US"),
                quality_notes=raw.get("quality_notes", ""),
                is_mock=False,
            ),
        )

    def get_quote(self, ticker: str) -> NormalizedQuote:
        symbol = ticker.upper().strip()
        try:
            cap = self.client.find_capability("market-data", ["quote", "price"])
            if cap:
                raw = self.client.call(cap, {"symbol": symbol})
                return self._normalize_quote(symbol, raw, cap)
            raise QverisApiError("No quote capability discovered")
        except (QverisNotConfiguredError, QverisApiError):
            return mock_data.get_mock_bundle(symbol).quote

    def get_price_history(self, ticker: str, days: int = 365) -> NormalizedPriceHistory:
        symbol = ticker.upper().strip()
        try:
            cap = self.client.find_capability("market-data", ["history", "historical", "ohlc"])
            if cap:
                raw = self.client.call(cap, {"symbol": symbol, "days": days})
                data = raw.get("data", raw)
                points = [
                    PricePoint(date=str(p.get("date", "")), close=float(p.get("close", 0.0)))
                    for p in data.get("points", data.get("candles", []))
                ]
                return NormalizedPriceHistory(
                    symbol=symbol,
                    points=points,
                    meta=DataPointMeta(capability_id=cap, symbol=symbol),
                )
            raise QverisApiError("No history capability discovered")
        except (QverisNotConfiguredError, QverisApiError):
            meta = DataPointMeta(
                provider="mock", symbol=symbol, is_mock=True,
                quality_notes="MOCK DATA — no price history available without QVeris.",
            )
            return NormalizedPriceHistory(symbol=symbol, points=[], meta=meta)

    def get_news(self, ticker: str) -> NormalizedNews:
        symbol = ticker.upper().strip()
        try:
            cap = self.client.find_capability("news", ["news", "sentiment"])
            if cap:
                raw = self.client.call(cap, {"symbol": symbol, "limit": 10})
                data = raw.get("data", raw)
                items = [
                    NewsItem(
                        title=str(n.get("title", "")),
                        summary=str(n.get("summary", n.get("description", ""))),
                        sentiment=str(n.get("sentiment", "neutral")),
                        published_at=n.get("published_at"),
                        source=str(n.get("source", "")),
                    )
                    for n in data.get("items", data.get("articles", []))
                ]
                return NormalizedNews(symbol=symbol, items=items, meta=DataPointMeta(capability_id=cap, symbol=symbol))
            raise QverisApiError("No news capability discovered")
        except (QverisNotConfiguredError, QverisApiError):
            return mock_data.get_mock_bundle(symbol).news

    def get_bundle(self, ticker: str) -> MarketDataBundle:
        """Fetch everything the analysis pipeline needs for one symbol."""
        symbol = ticker.upper().strip()
        if not self.client.is_configured:
            logger.info("QVeris not configured — serving MOCK DATA for %s", symbol)
            return mock_data.get_mock_bundle(symbol)
        quote = self.get_quote(symbol)
        profile = self.fundamentals.get_profile(symbol)
        fundamentals = self.fundamentals.get_fundamentals(symbol)
        news = self.get_news(symbol)
        is_mock = any(x.meta.is_mock for x in (quote, profile, fundamentals, news))
        return MarketDataBundle(quote=quote, profile=profile, fundamentals=fundamentals, news=news, is_mock=is_mock)

    def sources(self) -> list[dict]:
        """List discoverable data capabilities (or the mock source list)."""
        if not self.client.is_configured:
            return [
                {"capability_id": "mock.quote", "name": "Mock quote", "category": "market-data",
                 "description": "MOCK DATA — illustrative quote values."},
                {"capability_id": "mock.fundamentals", "name": "Mock fundamentals", "category": "fundamentals",
                 "description": "MOCK DATA — illustrative financial statements."},
                {"capability_id": "mock.news", "name": "Mock news", "category": "news",
                 "description": "MOCK DATA — placeholder news items."},
            ]
        try:
            return self.client.discover()
        except QverisApiError:
            return []
