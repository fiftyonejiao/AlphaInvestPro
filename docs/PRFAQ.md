# AlphaInvestPro — Press Release / FAQ

## Press Release

Today we are launching **AlphaInvestPro**, a simple AI-powered investment research interface that turns messy stock questions into structured investment memos. Users enter a company or ticker, choose a research depth, and receive a clear analysis of business quality, moat, valuation, risk, bull case, bear case, and final thesis.

Unlike generic AI chatbots, AlphaInvestPro does not hide reasoning in a wall of text. It shows each step of the analysis: quick screen, business quality review, valuation check, inversion/risk review, and final investment memo. The product is designed for clarity, discipline, and repeatable decision-making.

## FAQ

**Q: Is this a trading tool?**
No. AlphaInvestPro is research-only. There is no broker integration, no order execution, no strategy automation, and no autotrading anywhere in the product.

**Q: Where do the numbers come from?**
All market facts (quotes, fundamentals, profiles, news) come from the QVeris.ai data gateway, normalized into internal schemas with provenance metadata (provider, capability id, timestamps). If QVeris is not configured, the app runs on clearly-labeled `MOCK DATA`.

**Q: Does the AI make up the valuation?**
No. Every score and fair-value number is a deterministic calculation over normalized data, with assumptions listed by name, value, and source. The DeepSeek LLM only writes narrative commentary over those pre-computed results.

**Q: Which LLM does it use?**
DeepSeek only (`deepseek-chat` by default). There is no provider selector and no fallback to other model families. If no key is configured, narration is replaced with clearly-labeled `MOCK LLM OUTPUT`.

**Q: What languages does the interface support?**
English and 简体中文, switchable at any time without restarting or losing page state.

**Q: Is this financial advice?**
No. AI output and valuation assumptions may be wrong. Nothing in the product is a promise of profitability.
