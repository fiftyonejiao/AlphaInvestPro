"""Deterministic valuation with explicit assumptions and sources.

Every number in the fair-value range is a plain calculation over
normalized QVeris (or clearly-marked mock) data. Assumptions are listed
with name, value, and source so the user can audit and override them.
"""

from ..schemas.qveris import MarketDataBundle
from ..schemas.valuation import FairValueRange, Valuation, ValuationAssumption


def compute_valuation(bundle: MarketDataBundle) -> Valuation:
    f = bundle.fundamentals
    q = bundle.quote
    source = "MOCK DATA" if bundle.is_mock else f"QVeris ({f.meta.capability_id or 'fundamentals'})"
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
            ValuationAssumption(name="Free cash flow", value=f"{fcf:,.0f}", source=source),
            ValuationAssumption(name="Shares outstanding", value=f"{shares:,.0f}", source=source),
            ValuationAssumption(name="FCF per share", value=f"{fcf_per_share:,.2f}", source="derived"),
            ValuationAssumption(
                name="Required FCF yield (low/base/high price)",
                value="8.0% / 6.5% / 5.0%",
                source="manual assumption",
            ),
        ]
        method = "fcf_yield"
    elif eps and eps > 0:
        # Conservative / base / optimistic earnings multiples.
        low, base, high = eps * 12, eps * 18, eps * 24
        assumptions += [
            ValuationAssumption(name="EPS (trailing)", value=f"{eps:,.2f}", source=source),
            ValuationAssumption(
                name="Earnings multiple (low/base/high)",
                value="12x / 18x / 24x",
                source="manual assumption",
            ),
        ]
        method = "simple_multiple"
    else:
        price = q.price or 0.0
        low, base, high = price * 0.7, price, price * 1.3
        assumptions += [
            ValuationAssumption(name="Current price", value=f"{price:,.2f}", source=source),
            ValuationAssumption(
                name="Band around price (insufficient fundamentals)",
                value="-30% / 0% / +30%",
                source="manual assumption",
            ),
        ]
        method = "manual"

    assumptions.append(
        ValuationAssumption(
            name="Data timestamps",
            value=f"source: {f.meta.source_timestamp or 'n/a'}, retrieved: {f.meta.retrieval_timestamp}",
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
