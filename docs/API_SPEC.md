# AlphaInvestPro — API Spec

Base URL: `http://localhost:8000`

## Analysis jobs

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/analysis-jobs` | Create a job. Body: `{ticker, analysis_mode, language}`. Returns the job; analysis runs in the background. |
| GET | `/api/analysis-jobs` | List recent jobs. |
| GET | `/api/analysis-jobs/{job_id}` | Poll one job (status, current step, report id). |
| GET | `/api/analysis-jobs/{job_id}/events` | **SSE** stream of progress events. |
| GET | `/api/analysis-jobs/{job_id}/report` | Structured report for a completed job (409 if not ready). |

`analysis_mode`: `quick_screen | full_memo | risk_review | valuation_check`
`language`: `en | zh-CN` (controls memo language)

### SSE event shapes

```json
{"seq": 3, "event_type": "step_started",   "step": "quick_screen", "payload": {}, "created_at": "…"}
{"seq": 4, "event_type": "step_completed", "step": "quick_screen", "payload": {"passed": 5, "total": 6}, "created_at": "…"}
{"seq": 12, "event_type": "job_completed", "payload": {"report_id": "…"}, "created_at": "…"}
{"event_type": "stream_end", "status": "completed", "report_id": "…"}
```

## Reports

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/reports` | Report history (summaries). |
| GET | `/api/reports/{report_id}` | Full structured report + memo markdown. |

The report JSON follows the output schema in `docs/PROJECT_PROMPT.md` §15 (see `examples/sample_analysis_output.json`), plus provenance extras: `checklist`, `evidence_sources`, `is_mock_data`, `is_mock_llm`, `is_incomplete`, `language`, `generated_at`.

## Watchlist

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/watchlist` | Add `{ticker, company?, note?}` (idempotent per ticker). |
| GET | `/api/watchlist` | List items. |
| DELETE | `/api/watchlist/{item_id}` | Remove an item. |

## Market data (QVeris gateway)

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/market-data/qveris/status` | `{configured, base_url, session_id, mode: "live"|"mock"}`. |
| POST | `/api/market-data/qveris/fetch` | Body `{ticker}` → normalized quote/profile/fundamentals/news bundle. |
| GET | `/api/market-data/qveris/sources` | Discoverable capabilities (or the mock source list). |

## Settings

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/settings` | Stored defaults + DeepSeek/QVeris **status only** (never keys). |
| PUT | `/api/settings` | Update whitelisted keys: `default_language`, `default_analysis_mode`, `report_language_follows_ui`. |

## Misc

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/health` | `{status: "ok", research_only: true}`. |

Security notes: QVeris and DeepSeek API keys live only in backend environment variables; no endpoint returns them, and the frontend never receives them.
