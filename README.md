# AlphaInvestPro

**AlphaInvestPro** is a research-only, AI-powered investment analysis workbench. Enter a ticker, choose a research depth, and watch a visible agent workflow produce a structured investment memo: quick screen, business quality, moat, valuation with auditable assumptions, inversion/risk review, bull & bear cases, and a final verdict.

> **Not financial advice.** AlphaInvestPro is a research tool. AI output and valuation assumptions may be wrong. There is no trading execution anywhere in this product, and no promise of profitability.

The original Working-Backwards build specification lives in [`docs/PROJECT_PROMPT.md`](docs/PROJECT_PROMPT.md).

## Highlights

- **Visible agent workflow** — every analysis step streams live to the UI over Server-Sent Events; nothing hides in a wall of chat text.
- **Deterministic numbers, narrated by AI** — all scores, checklists, and fair-value ranges are plain calculations over normalized market data. The LLM only writes commentary and never invents a number.
- **QVeris.ai data gateway** — all financial stock data flows through a backend-only `QverisClient` (discover → inspect → call), normalized with full provenance (provider, capability id, timestamps). No key? The app runs on clearly labeled `MOCK DATA`.
- **DeepSeek-only LLM runtime** — a backend-only `DeepSeekClient` (`deepseek-chat` by default). No provider selector, no fallback model families. No key? Narration becomes clearly labeled `MOCK LLM OUTPUT` and everything else still works.
- **Bilingual GUI** — full interface switching between **English** and **简体中文**, persistent and instant, including memo language.
- **Auditable output** — every valuation shows its assumptions with sources; every report lists its evidence sources and timestamps; exports to Markdown and JSON.

## Quick start (local, no keys needed)

The app runs fully in demo mode without any API keys — mock data and mock LLM output are clearly labeled in the UI.

### Backend (FastAPI, Python 3.12+)

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js, Node 20+)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — you'll land on the dashboard.

### Docker Compose (alternative)

```bash
docker compose up
```

### Enable live data & AI narration

```bash
cp .env.example .env
# edit .env and set:
#   QVERIS_API_KEY=...    (financial data via QVeris.ai)
#   DEEPSEEK_API_KEY=...  (memo narration via DeepSeek)
```

Keys are read by the backend only and are never sent to the browser, logged, or embedded in reports.

## Usage

1. **New Analysis** — enter a ticker (try `AAPL`, `MSFT`, `KO`, `BRK.B`, `NVDA` in demo mode), pick a mode:
   - *Quick Screen* — fast pass/fail fundamentals checklist
   - *Full Memo* — the complete 10-step workflow
   - *Risk Review* — inversion-first risk analysis
   - *Valuation Check* — fair-value range with explicit assumptions
2. Watch the **agent timeline** stream each step live.
3. Read the **structured report**: checklist, quality & moat scores, valuation assumptions table, risk panel, bull/bear cases, final memo.
4. **Export** the memo as Markdown/JSON, add the ticker to your **watchlist**, and revisit everything under **Reports**.
5. Switch the whole GUI between **English / 简体中文** anytime from the top bar or Settings.

## Repository structure

```text
AlphaInvestPro/
  README.md
  docker-compose.yml
  .env.example
  backend/               FastAPI app
    app/
      api/               analysis_jobs, reports, watchlist, settings, market_data
      services/          analysis_orchestrator, buffett_skill_service, valuation_service,
                         qveris_client, deepseek_client, llm_service, market_data_service,
                         fundamentals_service, report_service, evidence_service
      schemas/           analysis, report, valuation, risk, qveris, llm
      storage/           database, models (SQLite via SQLAlchemy, PostgreSQL-ready)
    tests/               pytest suite (35 tests)
  frontend/              Next.js + TypeScript + Tailwind
    app/                 dashboard, analysis/new, analysis/[jobId], reports, reports/[reportId],
                         watchlist, settings
    components/          AnalysisStartForm, AnalysisTimeline, AgentStepCard, BuffettChecklist,
                         BusinessQualityCard, MoatScoreCard, ValuationAssumptionsTable,
                         RiskInversionPanel, BullBearCasePanel, FinalMemoViewer,
                         EvidenceSourceList, ExportReportButton, DeepSeekStatusBadge,
                         LanguageSwitcher, …
    lib/i18n.ts          two-locale i18n layer (en, zh-CN)
    locales/             en.json, zh-CN.json
  docs/                  PRFAQ, PRODUCT_SPEC, API_SPEC, UI_SPEC, PROJECT_PROMPT, REFERENCE_SOURCES
  examples/              sample_analysis_output.json (real pipeline output)
```

## API overview

`POST /api/analysis-jobs` · `GET /api/analysis-jobs/{id}` · `GET /api/analysis-jobs/{id}/events` (SSE) · `GET /api/analysis-jobs/{id}/report` · `GET /api/reports` · `GET /api/reports/{id}` · `POST|GET|DELETE /api/watchlist` · `GET /api/market-data/qveris/{status,sources}` · `POST /api/market-data/qveris/fetch` · `GET|PUT /api/settings` — full details in [`docs/API_SPEC.md`](docs/API_SPEC.md).

## Testing

```bash
cd backend && .venv/bin/python -m pytest tests/ -q   # 35 tests
cd frontend && npm run build                          # includes lint + type check
```

The test suite covers: QVeris client initialization, missing-key behavior, mock fallback, response normalization; DeepSeek missing-key behavior, model-family guard, proof that no non-DeepSeek provider code exists; the full orchestrator pipeline against the output schema; and every API endpoint.

## Safety & scope

- Research-only. No broker integration, order execution, strategy automation, backtesting workbench, or autotrading — by design.
- Deterministic calculations are never delegated to the LLM.
- Reports missing required financial fields are explicitly marked `INCOMPLETE`.
- API keys live in `.env` (backend only); `.env` is git-ignored.
