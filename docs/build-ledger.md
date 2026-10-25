# Build ledger

- Scope approved: Python + LangGraph + Streamlit; demo institution/market delegated by user.
- Ruling: Execute inline without another planning approval — user explicitly said proceed; avoids delaying the deadline.
- Existing workspace is empty and not a Git repository; create an independent local project under outputs.
- Local Python already has Streamlit 1.65.0, LangGraph 1.2.16, langchain-openai 1.7.2, httpx 0.28.1, Pydantic 2.14.1, python-dotenv 1.2.4. Use unittest to avoid unnecessary installations.
- API credentials absent at initial inspection; user will configure credentials and repair expired GitHub authentication. Do not claim live validation until performed.
- Task 1: 10 evidence/provider tests passed after initial missing-module RED run.
- Task 2: 16 total evidence/provider/graph tests passed; both recorded sample and outage sample generated through the real graph.
- UI verification initially stalled before app execution in Windows asyncio socket setup; granted network access resolved local socket creation. One UI test incorrectly reran an unsubmitted form; diagnostic output showed the checkbox was never submitted. Corrected the test to batch form value and submit, as the browser does.
- Task 3: 19/19 full-suite tests passed in 23.982 seconds, including all three Streamlit AppTest scenarios. Both recorded sample exports were reproduced.
- Final review: separate read-only reviewer found no actionable blocker; semantic grounding and live-provider/persistence limitations remain explicitly disclosed.
- User requested no Drive publication now. Keep the completed project narrative local and do not retry denied Drive writes.
- Packaging: Python AST parsing succeeded for all 13 Python files; ZIP integrity check passed for 31 project files and excludes .env, Git internals, virtual environments and caches. Local Git repository created on submission branch with an initial implementation commit; no remote push performed.
- Final browser finding: the native dataframe CSV toolbar offered a pre-approval export. Browser assertion reproduced it (1 control vs expected 0). Disable built-in data export/copy via Streamlit configuration, then verify the actual browser controls and rerun the suite before repackaging.
- Final fix verification: browser CSV assertion GREEN (0 controls); full suite 19/19 passed in 6.565 seconds. Local server health returned 200 and actual browser generated a four-institution, three-hypothesis brief awaiting review. ZIP repackaged after fix.
- Visual redesign requested by user: native navy sidebar/blue-gray workspace/teal palette; compact metric, comparison, opportunity and review cards. Full existing suite passed 19/19 in 6.739 seconds after the final layout changes. Browser appearance checked and pre-approval CSV control count remained zero. Submission archive refreshed; no credentials configured.
- Live setup: user supplied Tavily and OpenAI credentials locally and selected gpt-6-luna in .env. Tavily returned five official Truliant sources; authenticated OpenAI model listing included the configured model. No credential values were printed.
- Live compatibility fixes: reproduced unsupported temperature=0 for the reasoning model, then omitted sampling parameters for reasoning model families. A full-suite regression exposed an empty OPENAI_BASE_URL environment value overriding the SDK default; now pass the explicit default API URL when the custom endpoint is blank. Mock HTTP regression exercised both failures before fixes. Full suite passed 20/20 in 24.658 seconds. Live structured-response smoke passed; full Charlotte run in progress.
- First live browser run completed four profiles and three hypotheses in approximately 141 seconds from competitor confirmation, with 20/36 fields passing the initial lexical check. QA found incomplete fee conditions and an unidentified Skyla product, so the preliminary draft was not approved. Added full-page text collection with snippet fallback, conservative rejection of explicit uncertainty, and a product-identity gate; all three regressions failed before the fixes.
- Browser regression also reproduced dollar amounts rendered as math (2 math elements); literal currency escaping removed them (0 math elements). Manual replacement of a discovered candidate now drops the previous institution's rationale. No financial amounts or credentials were altered in the underlying evidence JSON.
# Public Modern Fintech revision — October 24, 2026

User selected Figma Option 3. Applied blue-gray/cobalt/navy theme, Inter and responsive cards while preserving evidence and human checkpoints. Removed web environment credential loading; added session password inputs and a clear action that discards graph/provider references and results. Added isolation/readiness/reset regressions, verified red then green. Full suite passed 26 tests; final browser check corrected narrow-screen metric clipping. Code review reported no blocking findings. Prepared Docker and Streamlit Cloud instructions. Hosting sign-in and expired GitHub auth block actual publication; no public URL claimed.


## Four-agent workflow release — October 24, 2026

Discovery, Research, Strategy and Benchmarks are logical roles within the LangGraph workflow. Strategy performs critique and at most one accepted revision. Original campaigns, review findings and final recommendations are retained. Human confirmation and export approval remain mandatory. In-app activity distinguishes local/replay operations from provider attempts and shows per-role usage, separate input/output cost estimates and explicit unknowns. No additional monitoring service or host credentials were added.

Final full suite: 41 tests passed in 12.706 seconds. New coverage includes usage retained before failed JSON parsing/retries, cache-sensitive pricing, missing usage/model pricing, partial cost subtotals, positive checking CPA acceptance, rejection of CPL relabeling and unsupported benchmark amounts, unsupported revision fallback, failed-review fallback, and UI display/approval isolation. Native browser QA reached review with one accepted revision, three campaign cards and locked exports.

Independent code review found two important defects. Both were reproduced by failing tests and fixed: missing cache/reasoning details now stay unknown, and checking CPA acceptance rejects lead/click units and unsupported funded/activated/opened account definitions. Lexical checks are conservative, not proof of semantic correctness; human source/comparability review remains required. No new paid live run was made for this release; HTTP/model boundaries and real graph/UI behavior were tested with fixtures/mocks.

Ruling: use the existing submission checkout and public app as authorized. Known model pricing only, dated official standard text snapshot; other models/unsupported tiers remain unpriced. The campaign-budget calculator and internal rate cards remain subsequent increments; this release delivers benchmark evidence and AI operating-cost tracking. No minor review findings were deferred.


## Cache-write accounting correction

Cache writes are now retained and priced as part of input, without double counting. The activity panel includes write tokens and write-cost components. Default 30m implicit writes and provider-reported mixed lifetime breakdowns are supported. Missing counts or unsupported pricing remain explicit unknowns. Historical incomplete runs must be rerun; no counts were invented. See [cache-cost accounting](docs/cache-costs.md) for formulas, assumptions and live verification.

Full suite: 49 tests passed in 13.875 seconds. Live probe: 1,683 input tokens, 1,680 cache writes and 203 output tokens; complete estimate $0.0003118. Independent review found no important issues. Existing submission branch and public app are updated as explicitly requested.
