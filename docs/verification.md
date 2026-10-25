# Verification record — October 24, 2026

## Observed automated results

Command: `python -m unittest discover -s tests -v`

Result: **19 tests passed**, 6.565 seconds in the final full run after the browser export-control fix (the preceding full run passed in 23.982 seconds). Python 3.12.10 on Windows. Streamlit's AppTest prints a benign “missing ScriptRunContext” warning for its main test thread; no app exception was reported.

Coverage includes:

- Exact source/quote/numeric grounding, invalid source IDs, domain lookalikes and unknown-not-zero behavior.
- Competitor count, identity/domain uniqueness, unsafe host rejection and blank input validation.
- Tavily HTTP adapter payload, official-domain filtering and malformed response rejection via MockTransport.
- Transient retry recovery, permanent failure after two attempts and sanitized operation traces.
- Real LangGraph execution, competitor interrupt before research, review interrupt before export, rejection and bounded follow-up research.
- A complete comparison with explicit unknowns after a simulated Skyla source outage.
- Removal of growth hypotheses citing fabricated sources.
- Actual Streamlit AppTest interaction: discover, confirm, review acknowledgment, approve/download, reject/reset and simulated outage.

## Reproducible samples

Commands:

```
python -m growth.cli --demo --approve-demo
python -m growth.cli --demo --approve-demo --outage
```

Both completed and generated Markdown and JSON under samples/. These are explicitly labeled recorded-evidence replays with scripted approval. They do not establish live Tavily/model correctness, latency or cost.

## Review

A separate read-only reviewer inspected the design and implementation and found no actionable blocker. The review confirmed the disclosed limitations: lexical evidence checks do not prove semantic correctness, live provider behavior remains unverified, and in-memory checkpoints disappear on restart. The reviewer's separately launched test run was not used as passing evidence; the completed main-session run above is the evidence.

Browser inspection found a Streamlit table-toolbar CSV export path before approval. A browser assertion reproduced it (one pre-approval CSV button, expected zero). Built-in table export/copy controls were then disabled using client.disableDataExport, preserving only the explicitly approved Markdown/JSON downloads. The same browser assertion then passed with zero CSV export buttons. This is a workflow guard, not prevention of screenshots or developer-tool access to displayed draft data.

The local Streamlit server started at http://127.0.0.1:8501. Its health endpoint returned HTTP 200. Browser interaction completed discovery, competitor confirmation and report generation to the human review gate; the rendered report showed four institution profiles and three hypotheses. A preview screenshot was saved beside the submission ZIP.

## Live status

An OpenAI + Tavily live Charlotte run was completed on October 24, 2026 using `gpt-6-luna`: four identified products, 16/36 supported fields and three hypotheses, observed complete within about three minutes after competitor confirmation. Offers/news and several product conditions remained unverified. The run was left at final human review. This was a partial research result, not independent validation of all product terms.

The public revision no longer loads saved credentials: each visitor must enter their own keys. GitHub access was subsequently renewed with explicit user approval and the app deployed publicly on October 24, 2026. Documentation was not published to Drive.

## Remaining acceptance checks

Configure credentials, complete one live run, manually inspect official source terms, record the model and elapsed time, review the final narrative, publish the repository with intended access, record a five-minute-or-less demo and submit the form. Software checks are not a research-quality benchmark or evidence of business uplift.

## Visual redesign verification

The requested navy sidebar, blue-gray workspace and teal accents were implemented through native Streamlit themes, bordered cards, badges and compact typography. Comparison, opportunity and review sections use distinct containers. The four summary cards remain in a compact row in the narrow app preview, while the sidebar collapses automatically on small screens.

After the final redesign changes, the full suite passed again: **19 tests in 6.739 seconds**. Browser inspection confirmed the navy research panel, compact metrics, dark comparison header, opportunity cards and review state. Built-in pre-approval CSV export controls remained absent (browser count: zero). No live provider calls or credential changes were performed.

## Option 3 and visitor credentials — October 24, 2026

Implemented selected Modern Fintech concept with native Streamlit theme/layout, Inter typography, cobalt actions, blue-gray background, navy sidebar and three opportunity cards. Regression tests first failed because visitor inputs did not exist, then passed after implementation. Full suite: **26 tests passed in 9.804 seconds**; no cleanup exception in that run. Tests cover no environment credential fallback, both-key readiness, isolated browser-session inputs, clearing graph/config/results with keys, recorded workflow, approval gates and provider grounding/retries. No additional paid live call was made for the visual/public revision.

A code review found no blocking credential-isolation issues. A mode-aware landing copy issue was corrected. Browser QA exercised the key-free recorded workflow to final review with approval unchecked. Container deployment files are prepared; the Docker image has not been built in this environment.

## Public release verification — October 24, 2026

URL: https://bank-cu-growth-intelligence.streamlit.app/ . GitHub source branch `submission` published from release commit `c71ec30`. Streamlit build logs confirm Python 3.12.15 and Streamlit 1.65.0. Sharing settings explicitly show **public and searchable**. Empty hosted API-key inputs disable live research; the hosted recorded demo reaches its confirmation and final review checkpoints. No API keys were entered as host secrets or into the hosted smoke test. Release test rerun: **26 tests passed in 38.602 seconds**. Submission ZIP integrity and exclusion of credential files and saved key values were checked before publication.


## Four-agent workflow release — October 24, 2026

Discovery, Research, Strategy and Benchmarks are logical roles within the LangGraph workflow. Strategy performs critique and at most one accepted revision. Original campaigns, review findings and final recommendations are retained. Human confirmation and export approval remain mandatory. In-app activity distinguishes local/replay operations from provider attempts and shows per-role usage, separate input/output cost estimates and explicit unknowns. No additional monitoring service or host credentials were added.

Final full suite: 41 tests passed in 12.706 seconds. New coverage includes usage retained before failed JSON parsing/retries, cache-sensitive pricing, missing usage/model pricing, partial cost subtotals, positive checking CPA acceptance, rejection of CPL relabeling and unsupported benchmark amounts, unsupported revision fallback, failed-review fallback, and UI display/approval isolation. Native browser QA reached review with one accepted revision, three campaign cards and locked exports.

Independent code review found two important defects. Both were reproduced by failing tests and fixed: missing cache/reasoning details now stay unknown, and checking CPA acceptance rejects lead/click units and unsupported funded/activated/opened account definitions. Lexical checks are conservative, not proof of semantic correctness; human source/comparability review remains required. No new paid live run was made for this release; HTTP/model boundaries and real graph/UI behavior were tested with fixtures/mocks.

Ruling: use the existing submission checkout and public app as authorized. Known model pricing only, dated official standard text snapshot; other models/unsupported tiers remain unpriced. The campaign-budget calculator and internal rate cards remain subsequent increments; this release delivers benchmark evidence and AI operating-cost tracking. No minor review findings were deferred.

Public deployment verified from functional commit `e40967a`: Streamlit initially hot-reloaded the new UI while retaining old imported workflow modules. Rebooted the existing public app, then started a fresh key-free recorded run, confirmed competitors and observed four-agent completion, one accepted revision, structured review findings and the activity panel's zero external API calls/$0 replay cost. Final approval remained unchecked and downloads locked. No hosted keys or secrets were added. Architecture notes and the credential-free submission ZIP were synchronized after verification.


## Cache-write accounting correction

Cache writes are now retained and priced as part of input, without double counting. The activity panel includes write tokens and write-cost components. Default 30m implicit writes and provider-reported mixed lifetime breakdowns are supported. Missing counts or unsupported pricing remain explicit unknowns. Historical incomplete runs must be rerun; no counts were invented. See [cache-cost accounting](docs/cache-costs.md) for formulas, assumptions and live verification.

Full suite: 49 tests passed in 13.875 seconds. Live probe: 1,683 input tokens, 1,680 cache writes and 203 output tokens; complete estimate $0.0003118. Independent review found no important issues. Existing submission branch and public app are updated as explicitly requested.


## Client selection and website confirmation

Research mode, client name, market, website lookup/confirmation, goals and start controls are now at the top of the main workspace. Keys/model/privacy remain in the sidebar. Switching modes or changing the live client/market discards the previous graph, demo/live report, approval, goals, website suggestion and confirmation. API keys stay until Clear keys & session. Mode selection and live name/market edits remain available while a report is open. No demo comparison or export survives switching to live.

Live users enter an FI name and market, request a likely official website, inspect its on-domain source, correct the domain if needed, and confirm before research. Failure permits manual domain entry followed by the same explicit confirmation. Changing identity, market or domain invalidates confirmation. Discovery preflight uses one search/model pair plus at most one on-domain follow-up when initial results are directories or otherwise ungrounded. It is part of Discovery, not a fifth agent. API attempts and costs feed the research run ledger; repeated user-triggered lookups also count.

Validation: 54 tests passed in 17.231 seconds, including main-area selection, demo-to-live reset, active-client edits, confirmation invalidation, manual readiness, domain/quote grounding, bounded directory recovery and existing approval/credential regressions. Independent review found no Important/Critical issues. Live lookup successfully returned a sourced Truliant website suggestion after two search/model pairs; user confirmation was not bypassed. No full live competitor run or report approval was needed for this revision.


## Local saved-key isolation

Added a separate loopback-only local_app.py and updated run.ps1. Public app.py never reads .env; saved settings are injected only by the guarded local launcher. Saved keys do not populate password widgets. Clear keys & session disables automatic fallback until explicitly restored. Independent security review found no important defects. The full suite passed 57 tests, covering local key readiness, clear behavior, non-loopback rejection before loading, public no-loader behavior and prior BYOK/session/export controls. The local server remains running for the user's United Heritage Credit Union test; the public deployment is untouched.


## Abbreviated website lookup and retry — October 25, 2026

Lookup expands standalone CU and FCU for search/model context while retaining user input. Both search and deterministic acceptance exclude common technical-hosting, directory and social domains. This prevents an on-domain identity quote from a hosting copy being accepted as the FI's official public domain. Unknown/provider-failure primary results receive one bounded alternative query; retry remains an explicit user action after exhaustion. No FI-domain mapping is hardcoded.

Failure state now persists across reruns and changes the primary action to Retry website lookup, with manual-domain fallback explained. Every retry clears stale suggestion/domain/confirmation, retains paid attempts in the run ledger, and still requires user confirmation. A wrong proposed domain can still constrain the bounded follow-up; retry and manual correction remain available. Network/provider success cannot be guaranteed.

Validation: 61 tests passed in 21.513 seconds, including abbreviation search, provider recovery, technical-host rejection, persistent retry UI and successful retry without auto-confirmation. A real short-name/no-market test returned uhcu.org with one search and one model operation (estimated model cost $0.00031355). Independent review found no important defects. Public app remains BYOK; local saved-key behavior is unchanged.


## Discovery to proposal decision October 25 2026

Added a live LangGraph discovery checkpoint after institution research. A typed goal/timeframe/problem/observation/success definition/confirmation must be provided before paid campaign drafting and benchmark work. Unknown or missing inputs yield deterministic questions, zero campaigns and no revision cycle; these are explicitly local checks, not model tool calls. Completed research is reused when the strategist refines discovery. Four logical agent roles and final approval-gated export remain. Recorded campaign outputs remain curated; the optional checkpoint is exposed in recorded setup.

Validation: the new graph regressions were observed failing before implementation. Final full suite passed 71 tests in 65.835 seconds; two UI tests passed after adding source inspection at the checkpoint. Coverage includes live omitted-input gating, canonical unknown handling, no confirmation bypass, unconfirmed export labels, resume without research, retained source profiles, approval and client reset. Independent review identified two defects (unknown-value readiness and export confirmation wording); both were fixed and re-reviewed with no important issue remaining. Browser verification observed research pause, incomplete submission, retained evidence and a Discovery needed decision with no campaigns. No fresh live provider run was performed for this release; existing provider integration remains, Strategy prompt changes require human review of generated recommendations.

Browser refinement also completed: an explicitly illustrative application-completion brief was confirmed after the unknown path; the existing research was retained and the recorded campaign/review branch resumed. Recommendation logic displayed the client problem, cited public evidence, intervention, channel role, agreed success definition and remaining constraints. No final approval was given.


## Proposal planner October 25 2026

Added deterministic funded-checking proposal scenarios: editable target, all-in CPA 300/450/600 and channel envelopes 70/30 or 60/25/15 when paid social is included. Numerical mix is a heuristic, not an industry benchmark. No extra included costs are added and no per-channel account forecasts are produced. Exact-cent allocation reconciles every scenario. Inputs and computed budgets persist only when saved; unsaved edits block approval and saving resets the review acknowledgement. Approved/rejected values are locked. Discovery refinement/client changes clear proposal state. Final approved Markdown/JSON include the saved scenario and provenance. No provider call or new agent is added.

Validation: calculator tests were observed failing before implementation. Six calculation/workflow and two native UI tests passed; the full suite passed 79 tests in 26.285 seconds. Tests cover CPA/mix validation, 500-account budgets, paid-social suggestions, editable targets, cent reconciliation, graph review interrupt preservation, gated export, unsaved-change blocking, saved-scenario locking and client reset. Independent review found no important concrete defect. Existing API/provider behavior is unchanged; no new live API call is required for deterministic planning.

Browser verification: the recorded report exposed Proposal planner; selecting paid social changed shares to 60/25/15. The 500-account base scenario displayed USD 225,000 total with USD 135,000 / 56,250 / 33,750 channel envelopes. Saving attached the scenario while leaving final approval pending. Preview/provenance and the distinction from AI costs remained visible.
