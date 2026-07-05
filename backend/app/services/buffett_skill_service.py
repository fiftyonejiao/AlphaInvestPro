"""Quality-lens scoring: quick screen, business quality, moat, management.

All scores are deterministic functions of normalized fundamentals — the
LLM never produces these numbers, it only narrates them afterwards.
"""

from ..schemas.analysis import BusinessQuality, ChecklistItem, Moat
from ..schemas.qveris import MarketDataBundle, NormalizedFundamentals


def _fmt_pct(v: float | None) -> str:
    return f"{v * 100:.1f}%" if v is not None else "n/a"


def quick_screen(f: NormalizedFundamentals) -> list[ChecklistItem]:
    """Quick screen: a short pass/fail checklist over the fundamentals."""
    items: list[ChecklistItem] = []

    def check(key: str, label: str, passed: bool, detail: str) -> None:
        items.append(ChecklistItem(key=key, label=label, passed=passed, detail=detail))

    check(
        "profitability", "Consistently profitable",
        (f.net_income or 0) > 0,
        f"Net income: {f.net_income:,.0f}" if f.net_income is not None else "Net income unavailable",
    )
    check(
        "roe", "Return on equity above 12%",
        (f.roe or 0) >= 0.12,
        f"ROE: {_fmt_pct(f.roe)}",
    )
    check(
        "margins", "Operating margin above 15%",
        (f.operating_margin or 0) >= 0.15,
        f"Operating margin: {_fmt_pct(f.operating_margin)}",
    )
    check(
        "fcf", "Positive free cash flow",
        (f.free_cash_flow or 0) > 0,
        f"FCF: {f.free_cash_flow:,.0f}" if f.free_cash_flow is not None else "FCF unavailable",
    )
    check(
        "debt", "Debt under control (D/E below 1.0 or high cash)",
        (f.debt_to_equity is not None and f.debt_to_equity < 1.0)
        or ((f.cash or 0) > (f.total_debt or 0)),
        f"Debt/Equity: {f.debt_to_equity if f.debt_to_equity is not None else 'n/a'}",
    )
    check(
        "growth", "Revenue growing (5y average above 3%)",
        (f.revenue_growth_5y or 0) >= 0.03,
        f"5y revenue growth: {_fmt_pct(f.revenue_growth_5y)}",
    )
    return items


def business_quality(bundle: MarketDataBundle) -> BusinessQuality:
    f = bundle.fundamentals
    points = 0.0
    evidence: list[str] = []

    if (f.roe or 0) >= 0.20:
        points += 2.5
        evidence.append(f"High return on equity ({_fmt_pct(f.roe)})")
    elif (f.roe or 0) >= 0.12:
        points += 1.5
        evidence.append(f"Solid return on equity ({_fmt_pct(f.roe)})")

    if (f.net_margin or 0) >= 0.20:
        points += 2.5
        evidence.append(f"Strong net margin ({_fmt_pct(f.net_margin)})")
    elif (f.net_margin or 0) >= 0.10:
        points += 1.5
        evidence.append(f"Healthy net margin ({_fmt_pct(f.net_margin)})")

    if (f.free_cash_flow or 0) > 0 and (f.net_income or 0) > 0:
        conversion = (f.free_cash_flow or 0) / (f.net_income or 1)
        if conversion >= 0.9:
            points += 2.5
            evidence.append(f"Excellent FCF conversion ({conversion:.0%} of net income)")
        elif conversion >= 0.6:
            points += 1.5
            evidence.append(f"Decent FCF conversion ({conversion:.0%} of net income)")

    if (f.revenue_growth_5y or 0) >= 0.10:
        points += 2.5
        evidence.append(f"Strong revenue growth ({_fmt_pct(f.revenue_growth_5y)} over 5y)")
    elif (f.revenue_growth_5y or 0) >= 0.03:
        points += 1.5
        evidence.append(f"Steady revenue growth ({_fmt_pct(f.revenue_growth_5y)} over 5y)")

    score = min(points, 10.0)
    if score >= 7.5:
        summary = "High-quality business with strong returns, margins, and cash generation."
    elif score >= 5.0:
        summary = "Reasonable business quality with some strong attributes and some average ones."
    else:
        summary = "Below-average business quality on the measured fundamentals."
    return BusinessQuality(score=round(score, 1), summary=summary, evidence=evidence)


def moat_review(bundle: MarketDataBundle) -> Moat:
    f = bundle.fundamentals
    points = 0.0
    risks: list[str] = []

    if (f.gross_margin or 0) >= 0.50:
        points += 3.0
    elif (f.gross_margin or 0) >= 0.35:
        points += 2.0
    else:
        risks.append("Low gross margin suggests limited pricing power.")

    if (f.roic or 0) >= 0.20:
        points += 3.5
    elif (f.roic or 0) >= 0.10:
        points += 2.0
    else:
        risks.append("Returns on invested capital do not clearly exceed cost of capital.")

    if (f.operating_margin or 0) >= 0.25:
        points += 3.5
    elif (f.operating_margin or 0) >= 0.15:
        points += 2.0
    else:
        risks.append("Thin operating margins leave little buffer against competition.")

    if not risks:
        risks.append("Even durable advantages can erode; monitor competitive dynamics.")

    score = min(points, 10.0)
    if score >= 7.5:
        summary = "Indicators consistent with a durable competitive advantage (high margins and returns on capital)."
    elif score >= 5.0:
        summary = "Some moat indicators present, but the advantage is not clearly durable."
    else:
        summary = "Weak moat indicators; the business may be competitively exposed."
    return Moat(score=round(score, 1), summary=summary, risks=risks)


def management_review(bundle: MarketDataBundle) -> dict:
    """Capital-allocation snapshot from balance-sheet posture."""
    f = bundle.fundamentals
    notes: list[str] = []
    if (f.cash or 0) > (f.total_debt or 0):
        notes.append("Net cash position — conservative balance sheet.")
    elif (f.debt_to_equity or 0) > 1.5:
        notes.append("Elevated leverage — capital allocation deserves scrutiny.")
    else:
        notes.append("Moderate leverage.")
    if (f.free_cash_flow or 0) > 0:
        notes.append("Positive free cash flow available for reinvestment or shareholder returns.")
    return {"notes": notes}
