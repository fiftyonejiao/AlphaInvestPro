# AlphaInvestPro — UI Spec

## Navigation

Top navigation: Dashboard · New Analysis · Watchlist · Reports · Settings, plus a `DeepSeekStatusBadge` and the persistent `LanguageSwitcher` (English / 简体中文). No trading, broker, backtesting, or execution pages exist.

## Pages

| Route | Purpose |
| --- | --- |
| `/dashboard` | Stats (report count, watchlist size, data/LLM mode badges) and recent reports. |
| `/analysis/new` | `AnalysisStartForm`: ticker input, four analysis-mode cards, report-language select. |
| `/analysis/[jobId]` | Live `AnalysisTimeline` of `AgentStepCard`s fed by the SSE stream; renders the full `ReportView` on completion. |
| `/reports` | Report history table (company, mode, verdict, confidence, date). |
| `/reports/[reportId]` | Full report view. |
| `/watchlist` | Add/remove tickers with notes; shows last verdict per ticker. |
| `/settings` | Language switcher, DeepSeek status (model, no provider selector), QVeris status, default analysis mode. |

## Components

`AnalysisStartForm`, `AnalysisTimeline`, `AgentStepCard`, `BuffettChecklist`, `BusinessQualityCard`, `MoatScoreCard`, `ValuationAssumptionsTable`, `RiskInversionPanel`, `BullBearCasePanel`, `FinalMemoViewer`, `EvidenceSourceList`, `ExportReportButton`, `DeepSeekStatusBadge`, `LanguageSwitcher` — plus shared `NavBar`, `ReportView`, `VerdictBadge`, `DisclaimerBanner`, and UI primitives.

## Report view composition

1. Header: company, ticker, verdict badge, confidence, `MOCK DATA` / `MOCK LLM OUTPUT` / `INCOMPLETE` badges, export + watchlist actions.
2. Quick-screen checklist (pass/fail with detail).
3. Business quality and moat score cards (0-10 with score bars and evidence/risks).
4. Valuation: method badge, low/base/high fair-value cells, full assumptions table (name / value / source).
5. Risk & inversion panel: top risks, thesis killers, highlighted inversion question.
6. Bull/bear two-column panel.
7. Final memo (rendered Markdown, follows report language).
8. Evidence source list with provider, capability id, retrieval timestamps, and mock flags.
9. Persistent research-only disclaimer footer on every page.

## i18n rules

- Two locales only: `en`, `zh-CN` (简体中文, not 繁體中文).
- All user-facing strings resolve through translation keys in `frontend/locales/*.json`; hardcoded strings fail review.
- Language choice persists in local storage; switching never reloads or loses page state.
- Browser language is only the first-visit default.

## Transparency rules

- Mock data and mock LLM output are always visibly labeled.
- Valuation numbers are never shown without their assumptions table.
- Every report shows its evidence sources and timestamps.
