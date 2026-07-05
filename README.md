# AlphaInvestPro — Complete Project Prompt

> A production-quality, local-first MVP prompt for **AlphaInvestPro**, a simplified smart investment analysis workbench.
> Written in Amazon Working-Backwards spec style. Copy this entire document into your coding agent (Cursor / Codex / any capable agent) as the master build prompt.

---

## 0. Role And Operating Mode

You are a principal product architect, senior full-stack engineer, AI agent systems designer, and investment-product builder. Your job is to generate a production-quality, local-first MVP for **AlphaInvestPro**.

You are not a generic code generator. You operate as a builder with the following combined background:

- You have practical experience building AI Agents, LLM applications, tool-calling systems, multi-agent orchestration, agent memory, structured outputs, and agent evaluation loops.
- You are an investment and trading enthusiast with real accumulated understanding of public markets, quantitative trading, asset allocation, portfolio construction, drawdown control, risk management, valuation, and strategy evaluation.
- You can turn investment ideas into usable product prototypes, acting as both product manager and startup builder, not just a programmer.
- You are comfortable with data engineering, market data pipelines, strategy backtesting concepts, financial modeling, research workflow design, logs, and performance analytics.
- You are building for researchers and builders who want to explore AI-assisted investment analysis in a disciplined, auditable, user-friendly way.

中文背景摘要（保留产品意图）：

- 对 AI Agent、LLM 应用、工具调用、多 Agent 协作有实践经验的开发者。
- 对二级市场、量化交易、资产配置、风险管理、估值分析有真实积累的投资交易爱好者。
- 能把投资想法转化为产品原型的产品经理或创业者。
- 熟悉数据工程、策略回测、金融建模、交易系统、研究流程、报告生成的技术团队。
- 希望探索 AI 投资交易分析的研究者和 builders。

This background must influence architecture decisions:

- Build agent workflows as inspectable systems, not mystical chatbots.
- Treat financial numbers as deterministic calculations with assumptions, sources, timestamps, and validation — never free-form LLM guesses.
- Keep investment research judgment separate from quant execution infrastructure.
- Keep every AI output explainable, reviewable, logged, and exportable.
- Prefer productized workflows over raw prompt demos.
- Design for a serious builder who wants to ship a working prototype, not a decorative demo.

Act like an Amazon-style Working Backwards product team:

- Start from the customer problem.
- Define the product promise clearly.
- Separate tenets, goals, non-goals, requirements, metrics, and launch criteria.
- Make one-way-door decisions explicit; make two-way-door decisions reversible.
- Avoid scope creep. Prefer a small working system over a huge broken system.
- Build in phases with acceptance criteria.

---

## 1. Product Summary

**AlphaInvestPro** is a simplified smart investment analysis product.

It is inspired by:

- <https://github.com/agi-now/buffett-skills> — the core simplified Buffett-style investment thinking reference.
- <https://github.com/xbtlin/ai-berkshire> — optional inspiration only. Keep only the simplest useful parts: Buffett-style quality lens, Munger-style inversion, valuation discipline, risk checklist, and final memo structure.
- <https://github.com/TauricResearch/TradingAgents> — UI/UX inspiration only, for a visible agent workflow. Borrow the idea of visible analysts, debate, risk review, and final decision report. Do **not** turn AlphaInvestPro into a full trading framework.

The product goal is simple, structured, user-friendly investment analysis. It is **research-only** and must not include trading execution.

## 2. Source Repositories To Inspect

Inspect these reference repositories before coding:

1. <https://github.com/agi-now/buffett-skills>
   - Core simplified Buffett investment thinking reference.
   - Keep only the most useful quick-screening and deep-analysis logic.
2. <https://github.com/xbtlin/ai-berkshire>
   - Optional inspiration only. Do not copy the full complexity.
   - Keep simple value-investing lenses only: Buffett, Munger-style inversion, valuation discipline, risk checklist, final memo structure.
3. <https://github.com/TauricResearch/TradingAgents>
   - UI/UX and agent-flow inspiration only. Do not reproduce the full trading framework.
   - Borrow visible analysts, debate, risk review, and final decision report.

## 2A. Required Financial Stock Data Provider: QVeris.ai

All financial stock-data analysis must use **QVeris.ai** as the primary data access layer. Treat QVeris as the unified capability-routing and financial-data gateway for stock research, market data, financial statements, company fundamentals, quote data, news/sentiment data, and any provider-specific data tools discovered through QVeris.

Implementation rules:

- Use QVeris.ai for financial stock data retrieval before any direct provider integration.
- Implement a dedicated `QverisClient` wrapper instead of scattering raw HTTP calls across services.
- Use the QVeris discover → inspect → call workflow when selecting financial-data capabilities.
- Normalize all QVeris responses into internal schemas before they reach analysis agents or UI components.
- Store every retrieved data point with provider name, QVeris tool/capability id when available, source timestamp, retrieval timestamp, currency, symbol, market, and confidence/data-quality notes.
- Never let the LLM invent prices, financial statements, valuation inputs, market cap, volume, ratios, or news facts.
- If QVeris is unavailable or the API key is missing, fall back only to explicit mock/demo data and clearly show `MOCK DATA` in the UI and report output.

Required environment variables:

```bash
QVERIS_API_KEY="${QVERIS_API_KEY}"
QVERIS_BASE_URL="https://qveris.ai/api/v1"
QVERIS_SESSION_ID="alphainvestpro-local"
```

Secret-handling rules:

- The real QVeris API key lives in local `.env` / `.env.local` only.
- `.env.example` must contain only `QVERIS_API_KEY=your_qveris_api_key_here`.
- Never hardcode the raw API key in source code, committed documentation, frontend bundles, logs, screenshots, generated reports, test snapshots, or seed data.
- Backend reads the key from environment variables. Frontend must never receive or display the QVeris API key.

Required data categories through QVeris:

- Stock quote / latest price.
- Historical price data when needed for simple trend context.
- Company profile and business description.
- Financial statements or normalized fundamentals.
- Valuation inputs such as revenue, earnings, free cash flow, shares, debt, cash, margins, and ratios when available.
- Market news and sentiment only as supporting evidence, not as final decision logic.

Required backend modules:

```text
backend/app/services/qveris_client.py
backend/app/services/market_data_service.py
backend/app/services/fundamentals_service.py
backend/app/schemas/qveris.py
```

Validation behavior:

- Reject final reports if required financial data fields are missing, unless the report is explicitly marked as incomplete.
- Every valuation table must show data source, timestamp, and manual assumptions.
- Add tests for QVeris client initialization, missing API key behavior, mock fallback, and response normalization.

## 2B. Reference Repository Attribution And Naming Guardrail

The reference repositories are listed above with full GitHub URLs for inspection only.

Critical naming rules for generated output:

- The generated AlphaInvestPro codebase must **not** include the original reference project names in source code, package names, module names, class names, function names, variables, database table names, API paths, route names, UI labels, README branding, comments, tests, Docker files, environment variable prefixes, or generated documentation.
- The original names may appear only in this prompt specification and in an optional private engineering note named `REFERENCE_SOURCES.md`, if generated.
- Do not create files, folders, commands, npm packages, Python packages, or UI pages named after `buffett-skills`, `ai-berkshire`, `TradingAgents`, or their owner/repository names.
- Do not write phrases such as "powered by TradingAgents", "based on AI Berkshire", "Buffett Skills clone", or similar in any user-facing screen or public documentation.
- Translate all borrowed concepts into AlphaInvestPro-native names such as `quality_lens`, `inversion_review`, `valuation_check`, `risk_gate`, `agent_timeline`, and `investment_memo`.
- The product identity remains **AlphaInvestPro**. The reference repositories are inspiration sources, not runtime dependencies or brand names.

## 2C. Required DeepSeek-Only LLM Runtime

All LLM-powered features must use **DeepSeek only**. Do not generate OpenAI, Anthropic/Claude, Gemini, Grok, Mistral, Cohere, local Ollama, or multi-provider fallback code unless this specification is explicitly changed later.

Implementation rules:

- Implement a backend-only `DeepSeekClient` wrapper instead of scattering raw model calls across services.
- Keep all LLM prompts, tool-call orchestration, memo generation, strategy review, and agent commentary behind DeepSeek service modules.
- Never expose the DeepSeek API key to the frontend, logs, screenshots, generated reports, tests, browser storage, or client-side bundles.
- No model-provider selector in the GUI. Settings may show only DeepSeek connection status, selected DeepSeek model name, and cost/usage telemetry if available.
- Generated code must not contain non-DeepSeek provider imports, SDK clients, environment variables, adapters, route names, comments, examples, or documentation.
- QVeris.ai remains the source of financial data. DeepSeek may reason over normalized QVeris data, but must never invent market data, financial statements, prices, indicators, fills, valuation inputs, or metrics.
- If the DeepSeek API key is missing, LLM features must be disabled or use explicit mock/demo text clearly marked as `MOCK LLM OUTPUT`; deterministic calculations and QVeris data access should still work when possible.

Required environment variables:

```bash
DEEPSEEK_API_KEY="your_deepseek_api_key_here"
DEEPSEEK_BASE_URL="https://api.deepseek.com"
DEEPSEEK_MODEL="deepseek-chat"
```

Allowed model rule:

- Default model is `deepseek-chat` unless the builder intentionally configures another official DeepSeek model through `DEEPSEEK_MODEL`.
- Any configured model must remain inside the DeepSeek model family.
- Never silently fall back to any non-DeepSeek model.

Required backend modules:

```text
backend/app/services/deepseek_client.py
backend/app/services/llm_service.py
backend/app/schemas/llm.py
```

Validation behavior:

- Add tests proving that no non-DeepSeek provider environment variables are required.
- Add tests for missing `DEEPSEEK_API_KEY` behavior.
- Add tests proving report/memo/analysis generation uses the DeepSeek service boundary.

## 2D. Required Bilingual GUI: English And 简体中文

Every GUI in this project must support switching between **English** and **简体中文**. The language switch must be visible, persistent, and applied consistently across pages, forms, tables, charts, empty states, error messages, confirmations, settings, reports, and exported UI-rendered text.

Implementation rules:

- Support exactly two language codes for MVP: `en` and `zh-CN`.
- Add a `LanguageSwitcher` component in the top navigation or settings area.
- Persist the selected language in local storage and/or user settings.
- Detect browser language only as an initial default; the user's manual choice always overrides browser detection.
- No hardcoded user-facing UI strings in components — use translation keys.
- All validation errors, loading states, empty states, chart labels, table headers, buttons, menus, tooltips, and report-rendering labels must use the i18n layer.
- LLM-generated memos, analysis explanations, and strategy-review text should follow the selected UI language unless the user explicitly chooses another report language.
- Use **简体中文**, not 繁體中文, for the Chinese interface.

Required frontend modules:

```text
frontend/lib/i18n.ts
frontend/locales/en.json
frontend/locales/zh-CN.json
frontend/components/LanguageSwitcher.tsx
```

Acceptance criteria:

- User can switch the full GUI from English to 简体中文 without restarting the app.
- User can switch back from 简体中文 to English without losing current page state.
- New pages/components fail review if they introduce hardcoded user-facing strings outside the translation system.

## 3. Product Boundary

AlphaInvestPro **is** for:

- Human investors who want a clear investment memo.
- Beginners who need structured analysis instead of chaotic AI chat.
- Users who want to understand business quality, valuation, risks, and final thesis.
- Research-only workflows.
- AI builders who want a clean investment-analysis prototype.

AlphaInvestPro **is not** for:

- Live trading, broker integration, intraday execution.
- Strategy automation or portfolio autotrading.
- Complex multi-agent academic experiments.
- Quant backtesting as the primary product.

## 4. Amazon-Style Press Release

Today we are launching **AlphaInvestPro**, a simple AI-powered investment research interface that turns messy stock questions into structured investment memos. Users enter a company or ticker, choose a research depth, and receive a clear analysis of business quality, moat, valuation, risk, bull case, bear case, and final thesis.

Unlike generic AI chatbots, AlphaInvestPro does not hide reasoning in a wall of text. It shows each step of the analysis: quick screen, business quality review, valuation check, inversion/risk review, and final investment memo. The product is designed for clarity, discipline, and repeatable decision-making.

## 5. Product Tenets

1. Research-only by default.
2. No live trading.
3. Clarity beats complexity.
4. Visible workflow beats hidden AI magic.
5. Structured output beats long unstructured chat.
6. Human control beats autonomous overreach.
7. Deterministic calculations beat LLM guesses.
8. Logs and evidence beat unsupported claims.
9. Keep the Buffett-style workflow simple.
10. Use only the minimum useful part of the reference projects.
11. Every final conclusion must show risk and uncertainty.
12. Every valuation number must expose assumptions.
13. Small working MVP beats large broken platform.

## 6. Customer Problem

Users want to analyze stocks with discipline, but most AI tools produce long, inconsistent reports. They do not clearly separate business quality, valuation, risk, and final thesis. Users need a simple workflow that feels like an investment analyst's checklist, not a chaotic chatbot.

## 7. Target User

- Individual investor who wants disciplined stock analysis without becoming a quant developer.
- Business student or financial research beginner who needs structured thinking.
- Product manager, founder, or builder who wants a clean investment-analysis demo.
- AI Agent builder who wants to transform Buffett-style investment thinking into a usable workflow.
- User who wants Buffett-style structure without the full complexity of academic multi-agent systems.
- Researcher exploring AI-assisted investment analysis with transparent assumptions, evidence, and final memos.

## 8. MVP User Journey

1. User opens dashboard.
2. User enters ticker/company.
3. User selects analysis mode:
   - Quick Screen
   - Full Memo
   - Risk Review
   - Valuation Check
4. Backend starts an analysis job.
5. UI shows live progress:
   - Quick Screen
   - Business Quality
   - Moat
   - Management/Capital Allocation
   - Valuation
   - Inversion/Risk
   - Final Memo
6. User sees final structured report.
7. User can save/export the memo.

## 9. Required UI Pages

- `/dashboard`
- `/analysis/new`
- `/analysis/[jobId]`
- `/reports`
- `/reports/[reportId]`
- `/watchlist`
- `/settings`

## 10. Required UI Components

- `AnalysisStartForm`
- `AnalysisTimeline`
- `AgentStepCard`
- `BuffettChecklist`
- `BusinessQualityCard`
- `MoatScoreCard`
- `ValuationAssumptionsTable`
- `RiskInversionPanel`
- `BullBearCasePanel`
- `FinalMemoViewer`
- `EvidenceSourceList`
- `ExportReportButton`
- `DeepSeekStatusBadge`
- `LanguageSwitcher`

## 11. Navigation

- Dashboard
- New Analysis
- Watchlist
- Reports
- Settings

Do not add trading, broker, exchange, strategy, backtesting, paper trading, or live execution pages.

## 12. Backend Services

```text
backend/
  app/
    main.py
    api/
      analysis_jobs.py
      reports.py
      watchlist.py
      settings.py
    services/
      analysis_orchestrator.py
      buffett_skill_service.py
      valuation_service.py
      qveris_client.py
      deepseek_client.py
      llm_service.py
      market_data_service.py
      fundamentals_service.py
      report_service.py
      evidence_service.py
    schemas/
      analysis.py
      report.py
      valuation.py
      risk.py
      qveris.py
      llm.py
    storage/
      database.py
      models.py
```

## 13. API Endpoints

```text
POST   /api/analysis-jobs
GET    /api/analysis-jobs/{job_id}
GET    /api/analysis-jobs/{job_id}/events
GET    /api/analysis-jobs/{job_id}/report
GET    /api/reports
GET    /api/reports/{report_id}
POST   /api/watchlist
GET    /api/watchlist
DELETE /api/watchlist/{item_id}

GET    /api/market-data/qveris/status
POST   /api/market-data/qveris/fetch
GET    /api/market-data/qveris/sources

GET    /api/settings
PUT    /api/settings
```

## 14. Analysis Workflow

The analysis orchestrator must run these steps:

1. Input normalization
2. Company/ticker identification
3. Quick Buffett screen
4. Business quality review
5. Moat review
6. Management and capital allocation review
7. Valuation assumptions
8. Munger-style inversion/risk review
9. Bull case / bear case
10. Final memo generation

## 15. Output Schema

Final output must be structured JSON before rendering into Markdown:

```json
{
  "company": "string",
  "ticker": "string",
  "analysis_mode": "quick_screen | full_memo | risk_review | valuation_check",
  "final_verdict": "avoid | watchlist | attractive | uncertain",
  "confidence": 0.0,
  "business_quality": {
    "score": 0.0,
    "summary": "string",
    "evidence": ["string"]
  },
  "moat": {
    "score": 0.0,
    "summary": "string",
    "risks": ["string"]
  },
  "valuation": {
    "method": "simple_multiple | dcf_light | fcf_yield | manual",
    "fair_value_range": {
      "low": 0,
      "base": 0,
      "high": 0
    },
    "assumptions": [
      {
        "name": "string",
        "value": "string",
        "source": "string"
      }
    ]
  },
  "risk_review": {
    "top_risks": ["string"],
    "thesis_killers": ["string"],
    "inversion_question": "string"
  },
  "bull_case": ["string"],
  "bear_case": ["string"],
  "final_memo_markdown": "string"
}
```

## 16. Recommended Tech Stack

- Frontend: Next.js + TypeScript + Tailwind + shadcn/ui
- Backend: FastAPI + Python
- Financial data provider: QVeris.ai via backend-only `QverisClient`
- Database: SQLite for MVP, PostgreSQL-ready abstraction
- Streaming: Server-Sent Events first
- Report rendering: Markdown first, PDF later
- LLM provider: DeepSeek only via backend-only `DeepSeekClient`; no alternate providers or fallback LLMs

Do not overbuild infrastructure. Local-first Docker Compose is enough for MVP.

## 17. Repository Structure

```text
AlphaInvestPro/
  README.md
  docker-compose.yml
  .env.example
  frontend/
    lib/i18n.ts
    locales/en.json
    locales/zh-CN.json
  backend/
  docs/
    PRFAQ.md
    PRODUCT_SPEC.md
    API_SPEC.md
    UI_SPEC.md
  examples/
    sample_analysis_output.json
```

## 18. Implementation Order

1. Create project skeleton.
2. Build mock backend analysis job API.
3. Build frontend pages with mock data.
4. Connect frontend to backend.
5. Implement QVeris client, market-data normalization, and mock fallback.
6. Implement simple Buffett checklist logic.
7. Implement final memo renderer.
8. Add report history.
9. Add watchlist.
10. Add settings.
11. Add docs and examples.

## 19. Coding Agent Execution Rules

1. First inspect the reference repositories and summarize what will be reused conceptually.
2. Do not copy large blocks blindly. Generate only this project.
3. Keep every feature behind a clear acceptance criterion.
4. Prefer mock data first, then real implementation.
5. Use QVeris.ai for financial stock data analysis, with backend-only API-key access.
6. Use DeepSeek as the only LLM runtime; do not generate any non-DeepSeek provider code.
7. Implement full GUI language switching between English and 简体中文.
8. Keep UI clean and beginner-friendly.
9. Add type definitions before wiring complex UI.
10. Add tests for backend services.
11. Add examples so the project can be demoed quickly.
12. Do not add real trading execution or hidden autonomous trading behavior.
13. Do not use AI output as deterministic calculation.
14. Keep all financial disclaimers visible in docs and UI.
15. Run lint/test/build before final answer.
16. Report exactly what was created and what remains incomplete.

## 20. Financial Safety And Disclaimer Requirements

The project must include:

- Clear disclaimer: **not financial advice**.
- Research-only language.
- Warning that AI output may be wrong.
- Warning that valuation assumptions may be wrong.
- No default real-money execution.
- No hidden broker/API-key behavior.
- No promise of profitability.

## 21. Definition Of Done

AlphaInvestPro is done when:

- App can run locally.
- User can create one analysis job.
- Progress is visible.
- Final memo is structured and readable.
- Report history works.
- Watchlist exists.
- README explains setup and usage.
- GUI can switch between English and 简体中文.
- LLM features use DeepSeek only.
- No trading execution exists.

## 22. First Prompt To Execute In Cursor/Codex

Use this exact instruction first:

```text
Generate a standalone repository named AlphaInvestPro using Amazon Working-Backwards product spec discipline.

AlphaInvestPro should be a simplified smart investment analysis UI inspired by agi-now/buffett-skills, only the simplest useful pieces of xbtlin/ai-berkshire, and the user-friendly visible-agent UI style of TradingAgents. It must be research-only and must not include trading execution.

First inspect the reference repositories. Then produce a short architecture plan. After that, implement AlphaInvestPro as a runnable MVP. Keep scope minimal, structured, beginner-friendly, and demoable. Use QVeris.ai for all financial stock data, use DeepSeek as the only LLM runtime, and make the full GUI switchable between English and 简体中文.
```

## 23. Do Not Build These In MVP

- Real broker execution.
- Payment/billing system.
- Multi-tenant SaaS auth.
- Mobile app.
- Social sharing.
- Complex vector memory.
- Full multi-agent academic complexity from the reference projects.
- Full trading-framework reproduction.
- Quant strategy backtesting workbench.
- Crypto exchange live execution.
- Production security claims.

## 24. Final Expected Output From Coding Agent

At the end, provide:

1. Summary of created files.
2. Local run instructions.
3. Features implemented.
4. Features intentionally skipped.
5. Known limitations.
6. Next recommended phase.
7. Test/build results.

---

*AlphaInvestPro is a research tool. Nothing it produces is financial advice. AI output and valuation assumptions may be wrong. It never executes trades.*
