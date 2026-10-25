# Demo readiness verification October 25 2026

## Verified scope

The supplied Market Research Agent Solution Kit Tavily Editable.docx is reference only. The application retains the agreed FI checking scope, OpenAI provider, four logical roles, review and one revision, and human gates. It does not implement the sample's Groq ReAct tool-selection loop, dedicated parallel web/news search, or guaranteed thirty-second completion. These are deliberate differences and must not be claimed in the presentation.

## Checks performed

- Full automated suite: 62 tests passed in 16.998 seconds after the final fix. Covers recorded end-to-end graph/UI, three competitors, review/revision, approval/rejection/export gates, client/mode reset, malformed provider output and bounded retries, evidence grounding, and input/output/cache-write cost arithmetic with explicit unknowns.
- Credential checks cover public BYOK without server environment fallback, loopback-only local saved-key loading, and clearing keys disabling local fallback.
- Live short-name website lookup returned United Heritage Credit Union, uhcu.org, with the official homepage identity quote. Browser confirmed the populated domain and unchecked confirmation after a clean server restart. One additional API probe used one search and one model call, 2,045 input and 109 output tokens, including 2,042 cache-write tokens; estimated model cost $0.00031005, search billed separately.
- Browser failure path retained the Retry website lookup action and manual-entry explanation across reruns. An old running process required restart after imported provider code changed; fresh startup loaded the fix. Restart after deployment rather than rely on hot reload across module changes.
- Read-only independent review found a follow-up extraction outage erased earlier grounded findings. A regression test failed before the change and passed afterward. The app now preserves the prior same-institution grounded profile on that failure, keeps the warning and unresolved gaps, and still requires human approval. Independent re-review found no important defect in this correction.
- The earlier live UHCU Austin full workflow completed with three campaigns, one revision, 28 API attempts, 108,590 input and 25,275 output tokens and estimated model cost $0.025041 including cache writes. This is earlier-run evidence, not a new full run performed during this QA pass.

## Demo limits and handoff

Review competitor identities, official domains and local relevance before confirming: discovery can suggest unsuitable institutions. Public funded-account CPA evidence can remain unavailable; no guaranteed acquisition budget or CPA calculator is implemented. Quote matching is not semantic or legal review. Live APIs can be slow or unavailable, so keep the explicitly labeled recorded demo as a fallback. Actual provider invoices may differ from the model-cost estimate; Tavily credits are separate.

The demo should show the client goal, official-domain confirmation, candidate correction, evidence and gaps, strategist takeaway, campaign concepts, review/revision, activity costs and final human gate. Do not portray recorded data as live or clicks as acquired accounts. No campaign is executed. User still owns recording and final submission.
