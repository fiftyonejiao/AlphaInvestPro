"""Company profile and fundamentals through QVeris, normalized before use."""

from typing import Optional

from ..schemas.qveris import CompanyProfile, DataPointMeta, NormalizedFundamentals
from . import mock_data
from .qveris_client import QverisApiError, QverisClient, QverisNotConfiguredError


class FundamentalsService:
    def __init__(self, client: Optional[QverisClient] = None):
        self.client = client or QverisClient()

    def get_profile(self, ticker: str) -> CompanyProfile:
        symbol = ticker.upper().strip()
        try:
            cap = self.client.find_capability("fundamentals", ["profile", "company", "overview"])
            if cap:
                raw = self.client.call(cap, {"symbol": symbol})
                data = raw.get("data", raw)
                return CompanyProfile(
                    symbol=symbol,
                    name=str(data.get("name", symbol)),
                    sector=str(data.get("sector", "")),
                    industry=str(data.get("industry", "")),
                    description=str(data.get("description", "")),
                    meta=DataPointMeta(
                        capability_id=cap,
                        symbol=symbol,
                        source_timestamp=data.get("timestamp") or raw.get("timestamp"),
                    ),
                )
            raise QverisApiError("No profile capability discovered")
        except (QverisNotConfiguredError, QverisApiError):
            return mock_data.get_mock_bundle(symbol).profile

    def get_fundamentals(self, ticker: str) -> NormalizedFundamentals:
        symbol = ticker.upper().strip()
        try:
            cap = self.client.find_capability("fundamentals", ["financial", "fundamental", "statement"])
            if cap:
                raw = self.client.call(cap, {"symbol": symbol})
                data = raw.get("data", raw)

                def num(key: str) -> Optional[float]:
                    v = data.get(key)
                    return float(v) if v is not None else None

                return NormalizedFundamentals(
                    symbol=symbol,
                    revenue=num("revenue"),
                    net_income=num("net_income"),
                    free_cash_flow=num("free_cash_flow"),
                    eps=num("eps"),
                    shares_outstanding=num("shares_outstanding"),
                    total_debt=num("total_debt"),
                    cash=num("cash"),
                    gross_margin=num("gross_margin"),
                    operating_margin=num("operating_margin"),
                    net_margin=num("net_margin"),
                    roe=num("roe"),
                    roic=num("roic"),
                    revenue_growth_5y=num("revenue_growth_5y"),
                    pe_ratio=num("pe_ratio"),
                    fcf_yield=num("fcf_yield"),
                    debt_to_equity=num("debt_to_equity"),
                    meta=DataPointMeta(
                        capability_id=cap,
                        symbol=symbol,
                        source_timestamp=data.get("timestamp") or raw.get("timestamp"),
                    ),
                )
            raise QverisApiError("No fundamentals capability discovered")
        except (QverisNotConfiguredError, QverisApiError):
            return mock_data.get_mock_bundle(symbol).fundamentals
