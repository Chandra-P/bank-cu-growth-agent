# Four-agent workflow and observability

Approved design: Discovery → human confirmation → Research → Strategy → Benchmarks → Strategy review → one revision → human approval. Checking only; direct mail, display and paid social. Same session-scoped BYOK model client, separate logical roles. No LangSmith service required.

Implementation sequence:
- Add regression tests for four-role routing, bounded review/revision, failure fallback, token accounting before parsing, cached-token pricing and unknown usage.
- Capture one sanitized event per provider attempt with role, operation, latency, usage and price provenance. No prompts, keys or raw exception text in events. Recorded mode has zero external calls and no fabricated tokens.
- Add benchmark extraction with exact source quote/numeric checks, explicit comparability and missing cost coverage. Never equate lead cost with funded-account CPA. No automatic adoption into a budget.
- Add review and revision as Strategy passes, retaining original draft and structured findings. Validate revised source references; preserve original if invalid or unavailable. Human approval remains mandatory.
- Finish client brief/takeaway/campaign cards and activity/cost panel. Campaign-budget calculator is a subsequent increment; this release adds benchmark evidence and AI operating costs, not an approved campaign quote.
- Run full tests, fresh independent review, browser QA, commit/push existing submission branch, verify hosted app, refresh submission bundle.

Ruling: reuse existing dedicated submission checkout and preserve earlier unpublished strategist-brief work. User explicitly authorized implementation and public update; no additional deployment approval needed.
Ruling: only exact known model pricing receives an automatic estimate; other models show unknown. Standard text pricing snapshot is dated and linked; unsupported billing tiers remain unpriced.
Review focus: retries and parsing failures must retain billed usage; no double-counted cache/reasoning tokens; rejected revisions cannot introduce unsupported source IDs; BYOK isolation/export approval and recorded-mode truthfulness must remain intact.
