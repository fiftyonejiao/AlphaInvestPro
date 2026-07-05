# Reference Sources (private engineering note)

AlphaInvestPro's concepts were inspired by the following repositories. Per the
naming guardrail in `docs/PROJECT_PROMPT.md` §2B, their names appear only in this
note and in the prompt spec — never in source code, branding, or UI.

- https://github.com/agi-now/buffett-skills — simplified quality-investing
  screening and deep-analysis structure (adapted into `buffett_skill_service`
  scoring, `quality_lens`-style checklist, and the memo layout).
- https://github.com/xbtlin/ai-berkshire — only the simplest useful lenses:
  quality lens, inversion review, valuation discipline, risk checklist, final
  memo structure.
- https://github.com/TauricResearch/TradingAgents — UI/UX inspiration for a
  visible agent workflow (agent timeline, staged analysis, final decision
  report). No trading-framework functionality was reproduced.

These repositories are inspiration sources, not runtime dependencies.
