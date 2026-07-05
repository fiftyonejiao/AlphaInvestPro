"""Quality-lens scoring: quick screen, business quality, moat, management.

All scores are deterministic functions of normalized fundamentals — the
LLM never produces these numbers, it only narrates them afterwards.
Human-readable labels/summaries are localized (en / zh-CN) so reports
follow the language selected for the analysis.
"""

from ..schemas.analysis import BusinessQuality, ChecklistItem, Moat
from ..schemas.qveris import MarketDataBundle, NormalizedFundamentals

_STRINGS = {
    "en": {
        "profitability": "Consistently profitable",
        "net_income": "Net income",
        "net_income_missing": "Net income unavailable",
        "roe_check": "Return on equity above 12%",
        "roe": "ROE",
        "margins_check": "Operating margin above 15%",
        "operating_margin": "Operating margin",
        "fcf_check": "Positive free cash flow",
        "fcf": "FCF",
        "fcf_missing": "FCF unavailable",
        "debt_check": "Debt under control (D/E below 1.0 or high cash)",
        "debt_to_equity": "Debt/Equity",
        "growth_check": "Revenue growing (5y average above 3%)",
        "growth": "5y revenue growth",
        "ev_roe_high": "High return on equity ({v})",
        "ev_roe_solid": "Solid return on equity ({v})",
        "ev_margin_strong": "Strong net margin ({v})",
        "ev_margin_healthy": "Healthy net margin ({v})",
        "ev_fcf_excellent": "Excellent FCF conversion ({v} of net income)",
        "ev_fcf_decent": "Decent FCF conversion ({v} of net income)",
        "ev_growth_strong": "Strong revenue growth ({v} over 5y)",
        "ev_growth_steady": "Steady revenue growth ({v} over 5y)",
        "quality_high": "High-quality business with strong returns, margins, and cash generation.",
        "quality_mid": "Reasonable business quality with some strong attributes and some average ones.",
        "quality_low": "Below-average business quality on the measured fundamentals.",
        "moat_risk_gross": "Low gross margin suggests limited pricing power.",
        "moat_risk_roic": "Returns on invested capital do not clearly exceed cost of capital.",
        "moat_risk_opmargin": "Thin operating margins leave little buffer against competition.",
        "moat_risk_default": "Even durable advantages can erode; monitor competitive dynamics.",
        "moat_high": "Indicators consistent with a durable competitive advantage (high margins and returns on capital).",
        "moat_mid": "Some moat indicators present, but the advantage is not clearly durable.",
        "moat_low": "Weak moat indicators; the business may be competitively exposed.",
        "mgmt_net_cash": "Net cash position — conservative balance sheet.",
        "mgmt_high_leverage": "Elevated leverage — capital allocation deserves scrutiny.",
        "mgmt_moderate": "Moderate leverage.",
        "mgmt_fcf": "Positive free cash flow available for reinvestment or shareholder returns.",
        "na": "n/a",
    },
    "zh-CN": {
        "profitability": "持续盈利",
        "net_income": "净利润",
        "net_income_missing": "净利润数据缺失",
        "roe_check": "净资产收益率高于 12%",
        "roe": "净资产收益率",
        "margins_check": "营业利润率高于 15%",
        "operating_margin": "营业利润率",
        "fcf_check": "自由现金流为正",
        "fcf": "自由现金流",
        "fcf_missing": "自由现金流数据缺失",
        "debt_check": "负债可控（负债/权益低于 1.0 或现金充裕）",
        "debt_to_equity": "负债/权益",
        "growth_check": "营收增长（5 年均值高于 3%）",
        "growth": "5 年营收增速",
        "ev_roe_high": "净资产收益率很高（{v}）",
        "ev_roe_solid": "净资产收益率稳健（{v}）",
        "ev_margin_strong": "净利率强劲（{v}）",
        "ev_margin_healthy": "净利率健康（{v}）",
        "ev_fcf_excellent": "自由现金流转化率优秀（约为净利润的 {v}）",
        "ev_fcf_decent": "自由现金流转化率尚可（约为净利润的 {v}）",
        "ev_growth_strong": "营收增长强劲（5 年 {v}）",
        "ev_growth_steady": "营收稳定增长（5 年 {v}）",
        "quality_high": "高质量企业：回报率、利润率与现金创造能力俱佳。",
        "quality_mid": "企业质量尚可：部分指标优秀，部分指标一般。",
        "quality_low": "按所测算的基本面指标，企业质量低于平均水平。",
        "moat_risk_gross": "毛利率偏低，定价权可能有限。",
        "moat_risk_roic": "投入资本回报率未明显超过资本成本。",
        "moat_risk_opmargin": "营业利润率单薄，面对竞争缓冲不足。",
        "moat_risk_default": "即使持久的优势也可能被侵蚀，需持续关注竞争格局。",
        "moat_high": "各项指标符合持久竞争优势特征（高利润率与高资本回报率）。",
        "moat_mid": "存在部分护城河迹象，但优势的持久性尚不明确。",
        "moat_low": "护城河指标偏弱，业务可能面临竞争暴露。",
        "mgmt_net_cash": "净现金状态——资产负债表保守。",
        "mgmt_high_leverage": "杠杆偏高——资本配置值得仔细审视。",
        "mgmt_moderate": "杠杆适中。",
        "mgmt_fcf": "自由现金流为正，可用于再投资或股东回报。",
        "na": "暂无",
    },
}


def _s(language: str) -> dict[str, str]:
    return _STRINGS.get(language, _STRINGS["en"])


def _fmt_pct(v: float | None, na: str) -> str:
    return f"{v * 100:.1f}%" if v is not None else na


def quick_screen(f: NormalizedFundamentals, language: str = "en") -> list[ChecklistItem]:
    """Quick screen: a short pass/fail checklist over the fundamentals."""
    S = _s(language)
    items: list[ChecklistItem] = []

    def check(key: str, label: str, passed: bool, detail: str) -> None:
        items.append(ChecklistItem(key=key, label=label, passed=passed, detail=detail))

    check(
        "profitability", S["profitability"],
        (f.net_income or 0) > 0,
        f"{S['net_income']}: {f.net_income:,.0f}" if f.net_income is not None else S["net_income_missing"],
    )
    check(
        "roe", S["roe_check"],
        (f.roe or 0) >= 0.12,
        f"{S['roe']}: {_fmt_pct(f.roe, S['na'])}",
    )
    check(
        "margins", S["margins_check"],
        (f.operating_margin or 0) >= 0.15,
        f"{S['operating_margin']}: {_fmt_pct(f.operating_margin, S['na'])}",
    )
    check(
        "fcf", S["fcf_check"],
        (f.free_cash_flow or 0) > 0,
        f"{S['fcf']}: {f.free_cash_flow:,.0f}" if f.free_cash_flow is not None else S["fcf_missing"],
    )
    check(
        "debt", S["debt_check"],
        (f.debt_to_equity is not None and f.debt_to_equity < 1.0)
        or ((f.cash or 0) > (f.total_debt or 0)),
        f"{S['debt_to_equity']}: {f.debt_to_equity if f.debt_to_equity is not None else S['na']}",
    )
    check(
        "growth", S["growth_check"],
        (f.revenue_growth_5y or 0) >= 0.03,
        f"{S['growth']}: {_fmt_pct(f.revenue_growth_5y, S['na'])}",
    )
    return items


def business_quality(bundle: MarketDataBundle, language: str = "en") -> BusinessQuality:
    S = _s(language)
    f = bundle.fundamentals
    points = 0.0
    evidence: list[str] = []

    if (f.roe or 0) >= 0.20:
        points += 2.5
        evidence.append(S["ev_roe_high"].format(v=_fmt_pct(f.roe, S["na"])))
    elif (f.roe or 0) >= 0.12:
        points += 1.5
        evidence.append(S["ev_roe_solid"].format(v=_fmt_pct(f.roe, S["na"])))

    if (f.net_margin or 0) >= 0.20:
        points += 2.5
        evidence.append(S["ev_margin_strong"].format(v=_fmt_pct(f.net_margin, S["na"])))
    elif (f.net_margin or 0) >= 0.10:
        points += 1.5
        evidence.append(S["ev_margin_healthy"].format(v=_fmt_pct(f.net_margin, S["na"])))

    if (f.free_cash_flow or 0) > 0 and (f.net_income or 0) > 0:
        conversion = (f.free_cash_flow or 0) / (f.net_income or 1)
        if conversion >= 0.9:
            points += 2.5
            evidence.append(S["ev_fcf_excellent"].format(v=f"{conversion:.0%}"))
        elif conversion >= 0.6:
            points += 1.5
            evidence.append(S["ev_fcf_decent"].format(v=f"{conversion:.0%}"))

    if (f.revenue_growth_5y or 0) >= 0.10:
        points += 2.5
        evidence.append(S["ev_growth_strong"].format(v=_fmt_pct(f.revenue_growth_5y, S["na"])))
    elif (f.revenue_growth_5y or 0) >= 0.03:
        points += 1.5
        evidence.append(S["ev_growth_steady"].format(v=_fmt_pct(f.revenue_growth_5y, S["na"])))

    score = min(points, 10.0)
    if score >= 7.5:
        summary = S["quality_high"]
    elif score >= 5.0:
        summary = S["quality_mid"]
    else:
        summary = S["quality_low"]
    return BusinessQuality(score=round(score, 1), summary=summary, evidence=evidence)


def moat_review(bundle: MarketDataBundle, language: str = "en") -> Moat:
    S = _s(language)
    f = bundle.fundamentals
    points = 0.0
    risks: list[str] = []

    if (f.gross_margin or 0) >= 0.50:
        points += 3.0
    elif (f.gross_margin or 0) >= 0.35:
        points += 2.0
    else:
        risks.append(S["moat_risk_gross"])

    if (f.roic or 0) >= 0.20:
        points += 3.5
    elif (f.roic or 0) >= 0.10:
        points += 2.0
    else:
        risks.append(S["moat_risk_roic"])

    if (f.operating_margin or 0) >= 0.25:
        points += 3.5
    elif (f.operating_margin or 0) >= 0.15:
        points += 2.0
    else:
        risks.append(S["moat_risk_opmargin"])

    if not risks:
        risks.append(S["moat_risk_default"])

    score = min(points, 10.0)
    if score >= 7.5:
        summary = S["moat_high"]
    elif score >= 5.0:
        summary = S["moat_mid"]
    else:
        summary = S["moat_low"]
    return Moat(score=round(score, 1), summary=summary, risks=risks)


def management_review(bundle: MarketDataBundle, language: str = "en") -> dict:
    """Capital-allocation snapshot from balance-sheet posture."""
    S = _s(language)
    f = bundle.fundamentals
    notes: list[str] = []
    if (f.cash or 0) > (f.total_debt or 0):
        notes.append(S["mgmt_net_cash"])
    elif (f.debt_to_equity or 0) > 1.5:
        notes.append(S["mgmt_high_leverage"])
    else:
        notes.append(S["mgmt_moderate"])
    if (f.free_cash_flow or 0) > 0:
        notes.append(S["mgmt_fcf"])
    return {"notes": notes}
