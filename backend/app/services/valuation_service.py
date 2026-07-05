"""Deterministic valuation with explicit assumptions and sources.

Every number in the fair-value range is a plain calculation over
normalized QVeris (or clearly-marked mock) data. Assumptions are listed
with name, value, and source so the user can audit and override them.
Assumption labels are localized (en / zh-CN) to follow the report language.
"""

from ..schemas.qveris import MarketDataBundle
from ..schemas.valuation import FairValueRange, Valuation, ValuationAssumption

_STRINGS = {
    "en": {
        "mock_source": "MOCK DATA",
        "derived": "derived",
        "manual": "manual assumption",
        "fcf": "Free cash flow",
        "shares": "Shares outstanding",
        "fcf_per_share": "FCF per share",
        "required_yield": "Required FCF yield (low/base/high price)",
        "eps": "EPS (trailing)",
        "multiple": "Earnings multiple (low/base/high)",
        "price": "Current price",
        "band": "Band around price (insufficient fundamentals)",
        "timestamps": "Data timestamps",
        "ts_value": "source: {src}, retrieved: {ret}",
    },
    "zh-CN": {
        "mock_source": "MOCK DATA（模拟数据）",
        "derived": "推导值",
        "manual": "人工假设",
        "fcf": "自由现金流",
        "shares": "总股本",
        "fcf_per_share": "每股自由现金流",
        "required_yield": "要求自由现金流收益率（低/基准/高价位）",
        "eps": "每股收益（过去 12 个月）",
        "multiple": "市盈率倍数（低/基准/高）",
        "price": "当前价格",
        "band": "围绕现价的区间（基本面数据不足）",
        "timestamps": "数据时间戳",
        "ts_value": "数据源时间：{src}，获取时间：{ret}",
    },
}


def compute_valuation(bundle: MarketDataBundle, language: str = "en") -> Valuation:
    S = _STRINGS.get(language, _STRINGS["en"])
    f = bundle.fundamentals
    q = bundle.quote
    source = S["mock_source"] if bundle.is_mock else f"QVeris ({f.meta.capability_id or 'fundamentals'})"
    assumptions: list[ValuationAssumption] = []

    # Prefer FCF yield when FCF and market cap are available; fall back to
    # a simple earnings multiple; last resort is the current price band.
    fcf = f.free_cash_flow
    shares = f.shares_outstanding
    eps = f.eps

    if fcf and shares and fcf > 0 and shares > 0:
        fcf_per_share = fcf / shares
        # Required FCF yields: 5% (high price), 6.5% (base), 8% (low/conservative).
        low, base, high = fcf_per_share / 0.08, fcf_per_share / 0.065, fcf_per_share / 0.05
        assumptions += [
            ValuationAssumption(name=S["fcf"], value=f"{fcf:,.0f}", source=source),
            ValuationAssumption(name=S["shares"], value=f"{shares:,.0f}", source=source),
            ValuationAssumption(name=S["fcf_per_share"], value=f"{fcf_per_share:,.2f}", source=S["derived"]),
            ValuationAssumption(name=S["required_yield"], value="8.0% / 6.5% / 5.0%", source=S["manual"]),
        ]
        method = "fcf_yield"
    elif eps and eps > 0:
        # Conservative / base / optimistic earnings multiples.
        low, base, high = eps * 12, eps * 18, eps * 24
        assumptions += [
            ValuationAssumption(name=S["eps"], value=f"{eps:,.2f}", source=source),
            ValuationAssumption(name=S["multiple"], value="12x / 18x / 24x", source=S["manual"]),
        ]
        method = "simple_multiple"
    else:
        price = q.price or 0.0
        low, base, high = price * 0.7, price, price * 1.3
        assumptions += [
            ValuationAssumption(name=S["price"], value=f"{price:,.2f}", source=source),
            ValuationAssumption(name=S["band"], value="-30% / 0% / +30%", source=S["manual"]),
        ]
        method = "manual"

    assumptions.append(
        ValuationAssumption(
            name=S["timestamps"],
            value=S["ts_value"].format(src=f.meta.source_timestamp or "n/a", ret=f.meta.retrieval_timestamp),
            source=source,
        )
    )

    return Valuation(
        method=method,
        fair_value_range=FairValueRange(low=round(low, 2), base=round(base, 2), high=round(high, 2)),
        assumptions=assumptions,
    )


def price_vs_value(bundle: MarketDataBundle, valuation: Valuation) -> dict:
    """Margin-of-safety context for the verdict logic."""
    price = bundle.quote.price or 0.0
    base = valuation.fair_value_range.base or 1.0
    discount = (base - price) / base if base else 0.0
    return {"price": price, "base_value": base, "discount_to_base": round(discount, 4)}
