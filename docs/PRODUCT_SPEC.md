# AlphaInvestPro — Product Spec (MVP)

## Product boundary

**For:** individual investors who want disciplined memos, beginners who need structure, builders who want a clean AI-investment-analysis prototype, research-only workflows.

**Not for:** live trading, broker integration, intraday execution, strategy automation, portfolio autotrading, quant backtesting as the primary product.

## Tenets

1. Research-only by default. 2. No live trading. 3. Clarity beats complexity. 4. Visible workflow beats hidden AI magic. 5. Structured output beats unstructured chat. 6. Human control beats autonomous overreach. 7. Deterministic calculations beat LLM guesses. 8. Logs and evidence beat unsupported claims. 9. Every conclusion shows risk and uncertainty. 10. Every valuation exposes assumptions. 11. Small working MVP beats large broken platform.

## User journey

1. Open dashboard → 2. Enter ticker → 3. Pick analysis mode (Quick Screen / Full Memo / Risk Review / Valuation Check) → 4. Backend starts a job → 5. UI streams live step progress over SSE → 6. Structured final report renders → 7. Save/export the memo, optionally add ticker to watchlist.

## Analysis workflow (orchestrator steps)

1. Input normalization
2. Company/ticker identification (QVeris fetch)
3. Quick screen (deterministic checklist)
4. Business quality review (deterministic score)
5. Moat review (deterministic score)
6. Management & capital allocation review
7. Valuation assumptions (fcf_yield / simple_multiple / manual, deterministic)
8. Inversion/risk review
9. Bull case / bear case
10. Final memo generation (DeepSeek narration over deterministic results)

Modes run subsets: `quick_screen` and `valuation_check` skip the deep steps they don't need.

## Verdict logic (deterministic)

- `attractive`: strong business (quality ≥ 6.5, moat ≥ 6.0, screen ≥ 2/3 passed) AND price ≥ 10% below base fair value.
- `watchlist`: strong business, but no margin of safety.
- `avoid`: weak screen (< 40% passed) or weak quality and moat.
- `uncertain`: everything else, and always when required data is missing.

## Data & LLM rules

- QVeris.ai is the only financial-data gateway; responses are normalized before use; every data point carries provenance (provider, capability id, source/retrieval timestamps, currency, symbol, market, quality notes).
- Missing QVeris key → explicit `MOCK DATA` mode, labeled in UI and memos.
- DeepSeek is the only LLM runtime; missing key → explicit `MOCK LLM OUTPUT`, deterministic pipeline still works.
- The LLM never produces numbers used in scores, valuations, or verdicts.
- Reports with missing required financial fields are marked `INCOMPLETE`.

## Bilingual GUI

- Exactly two locales: `en`, `zh-CN`. Persistent `LanguageSwitcher` in the top navigation.
- Browser language is only the initial default; user choice persists in local storage and always wins.
- No hardcoded user-facing strings; everything goes through `frontend/lib/i18n.ts` + `frontend/locales/*.json`.
- Report/memo language follows the language selected when starting the analysis.

## Definition of done

- App runs locally; a job can be created; progress is visible; the final memo is structured and readable; report history works; watchlist exists; README explains setup; GUI switches between English and 简体中文; LLM features use DeepSeek only; no trading execution exists.

## Explicit non-goals for MVP

Broker execution, payments, multi-tenant auth, mobile app, social sharing, vector memory, multi-agent academic complexity, quant backtesting workbench, crypto execution, production security claims.
