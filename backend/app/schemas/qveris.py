"""Normalized schemas for data retrieved through the QVeris gateway.

Every data point carries provenance metadata: provider, capability id,
source/retrieval timestamps, currency, symbol, market, and quality notes.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DataPointMeta(BaseModel):
    provider: str = "qveris"
    capability_id: Optional[str] = None
    source_timestamp: Optional[str] = None
    retrieval_timestamp: str = Field(default_factory=utc_now_iso)
    currency: str = "USD"
    symbol: str = ""
    market: str = "US"
    quality_notes: str = ""
    is_mock: bool = False


class NormalizedQuote(BaseModel):
    symbol: str
    price: float
    change_percent: Optional[float] = None
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    meta: DataPointMeta


class PricePoint(BaseModel):
    date: str
    close: float


class NormalizedPriceHistory(BaseModel):
    symbol: str
    points: list[PricePoint] = []
    meta: DataPointMeta


class CompanyProfile(BaseModel):
    symbol: str
    name: str
    sector: str = ""
    industry: str = ""
    description: str = ""
    meta: DataPointMeta


class NormalizedFundamentals(BaseModel):
    symbol: str
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    free_cash_flow: Optional[float] = None
    eps: Optional[float] = None
    shares_outstanding: Optional[float] = None
    total_debt: Optional[float] = None
    cash: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roe: Optional[float] = None
    roic: Optional[float] = None
    revenue_growth_5y: Optional[float] = None
    pe_ratio: Optional[float] = None
    fcf_yield: Optional[float] = None
    debt_to_equity: Optional[float] = None
    meta: DataPointMeta


class NewsItem(BaseModel):
    title: str
    summary: str = ""
    sentiment: str = "neutral"
    published_at: Optional[str] = None
    source: str = ""


class NormalizedNews(BaseModel):
    symbol: str
    items: list[NewsItem] = []
    meta: DataPointMeta


class QverisCapability(BaseModel):
    capability_id: str
    name: str
    category: str
    description: str = ""


class QverisStatus(BaseModel):
    configured: bool
    base_url: str
    session_id: str
    mode: str  # "live" | "mock"


class MarketDataBundle(BaseModel):
    """Everything the analysis pipeline needs for one symbol."""

    quote: NormalizedQuote
    profile: CompanyProfile
    fundamentals: NormalizedFundamentals
    news: NormalizedNews
    is_mock: bool = False
