"""Render the structured report JSON into a readable Markdown memo."""

from ..schemas.analysis import AnalysisReport

_LABELS = {
    "en": {
        "memo": "Investment Memo",
        "verdict": "Final Verdict",
        "confidence": "Confidence",
        "mode": "Analysis Mode",
        "quality": "Business Quality",
        "moat": "Moat",
        "valuation": "Valuation",
        "method": "Method",
        "range": "Fair Value Range (low / base / high)",
        "assumptions": "Assumptions",
        "risk": "Risk & Inversion Review",
        "top_risks": "Top Risks",
        "killers": "Thesis Killers",
        "inversion": "Inversion Question",
        "bull": "Bull Case",
        "bear": "Bear Case",
        "evidence": "Evidence & Data Sources",
        "checklist": "Quick Screen Checklist",
        "pass": "PASS",
        "fail": "FAIL",
        "mock_banner": "> **MOCK DATA** — QVeris is not configured. All figures are illustrative demo values.",
        "mock_llm_banner": "> **MOCK LLM OUTPUT** — DeepSeek is not configured. Narration is placeholder text.",
        "incomplete_banner": "> **INCOMPLETE REPORT** — required financial fields were missing.",
        "disclaimer": (
            "---\n*AlphaInvestPro is a research tool. This memo is not financial advice. "
            "AI output and valuation assumptions may be wrong. Nothing here is a promise of profitability.*"
        ),
        "verdicts": {"avoid": "Avoid", "watchlist": "Watchlist", "attractive": "Attractive", "uncertain": "Uncertain"},
    },
    "zh-CN": {
        "memo": "投资备忘录",
        "verdict": "最终结论",
        "confidence": "置信度",
        "mode": "分析模式",
        "quality": "商业质量",
        "moat": "护城河",
        "valuation": "估值",
        "method": "估值方法",
        "range": "合理价值区间（低 / 基准 / 高）",
        "assumptions": "假设",
        "risk": "风险与逆向审视",
        "top_risks": "主要风险",
        "killers": "论点致命项",
        "inversion": "逆向问题",
        "bull": "多头观点",
        "bear": "空头观点",
        "evidence": "证据与数据来源",
        "checklist": "快速筛查清单",
        "pass": "通过",
        "fail": "未通过",
        "mock_banner": "> **MOCK DATA（模拟数据）** — 未配置 QVeris，所有数字均为演示用途。",
        "mock_llm_banner": "> **MOCK LLM OUTPUT（模拟输出）** — 未配置 DeepSeek，叙述为占位文本。",
        "incomplete_banner": "> **报告不完整** — 缺少必需的财务字段。",
        "disclaimer": (
            "---\n*AlphaInvestPro 是研究工具。本备忘录不构成投资建议。"
            "AI 输出与估值假设可能有误，本工具不承诺任何盈利。*"
        ),
        "verdicts": {"avoid": "回避", "watchlist": "观察", "attractive": "有吸引力", "uncertain": "不确定"},
    },
}


def render_memo_markdown(report: AnalysisReport, narration: dict[str, str] | None = None) -> str:
    L = _LABELS.get(report.language, _LABELS["en"])
    narration = narration or {}
    lines: list[str] = []

    lines.append(f"# {report.company} ({report.ticker}) — {L['memo']}")
    lines.append("")
    if report.is_mock_data:
        lines.append(L["mock_banner"])
    if report.is_mock_llm:
        lines.append(L["mock_llm_banner"])
    if report.is_incomplete:
        lines.append(L["incomplete_banner"])
    lines.append("")
    lines.append(f"**{L['verdict']}:** {L['verdicts'].get(report.final_verdict, report.final_verdict)}  ")
    lines.append(f"**{L['confidence']}:** {report.confidence:.0%}  ")
    lines.append(f"**{L['mode']}:** `{report.analysis_mode}`")
    lines.append("")

    if report.checklist:
        lines.append(f"## {L['checklist']}")
        for item in report.checklist:
            mark = "✅" if item.passed else "❌"
            status = L["pass"] if item.passed else L["fail"]
            lines.append(f"- {mark} **{item.label}** — {status}. {item.detail}")
        lines.append("")

    lines.append(f"## {L['quality']} — {report.business_quality.score}/10")
    lines.append(report.business_quality.summary)
    for e in report.business_quality.evidence:
        lines.append(f"- {e}")
    if narration.get("business_quality"):
        lines.append("")
        lines.append(narration["business_quality"])
    lines.append("")

    lines.append(f"## {L['moat']} — {report.moat.score}/10")
    lines.append(report.moat.summary)
    for r in report.moat.risks:
        lines.append(f"- ⚠️ {r}")
    lines.append("")

    v = report.valuation
    lines.append(f"## {L['valuation']}")
    lines.append(f"**{L['method']}:** `{v.method}`  ")
    fr = v.fair_value_range
    lines.append(f"**{L['range']}:** {fr.low:,.2f} / {fr.base:,.2f} / {fr.high:,.2f}")
    lines.append("")
    lines.append(f"**{L['assumptions']}:**")
    lines.append("")
    lines.append("| # | Name | Value | Source |")
    lines.append("| --- | --- | --- | --- |")
    for i, a in enumerate(v.assumptions, 1):
        lines.append(f"| {i} | {a.name} | {a.value} | {a.source} |")
    lines.append("")

    rr = report.risk_review
    lines.append(f"## {L['risk']}")
    lines.append(f"**{L['top_risks']}:**")
    for r in rr.top_risks:
        lines.append(f"- {r}")
    lines.append(f"**{L['killers']}:**")
    for r in rr.thesis_killers:
        lines.append(f"- {r}")
    lines.append(f"**{L['inversion']}:** {rr.inversion_question}")
    lines.append("")

    lines.append(f"## {L['bull']}")
    for b in report.bull_case:
        lines.append(f"- {b}")
    lines.append("")
    lines.append(f"## {L['bear']}")
    for b in report.bear_case:
        lines.append(f"- {b}")
    lines.append("")

    if narration.get("final_memo"):
        lines.append(narration["final_memo"])
        lines.append("")

    lines.append(f"## {L['evidence']}")
    for s in report.evidence_sources:
        mock = " **[MOCK DATA]**" if s.is_mock else ""
        cap = f", capability `{s.capability_id}`" if s.capability_id else ""
        lines.append(f"- {s.name}: provider `{s.provider}`{cap}, retrieved {s.retrieval_timestamp}{mock}")
    lines.append("")
    lines.append(L["disclaimer"])
    return "\n".join(lines)
