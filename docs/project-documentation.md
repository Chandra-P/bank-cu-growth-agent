# Bank & Credit Union Growth Intelligence Agent

Week 3 / Project A — Market Research Agent: Competitor Analysis

## Project overview

This project helps bank and credit union growth teams research competing checking products and decide what acquisition ideas to test. The demo uses Truliant Federal Credit Union in Charlotte, North Carolina, with Truist, Bank of America and Skyla Credit Union as illustrative competitors. The user confirms the comparison set; the system does not claim a verified market-share ranking.

## Agent one-liner

My agent helps a bank or credit union growth professional compare three competitors' checking offers in a web app, replacing manual product-page research and comparison assembly. It discovers candidates, searches official domains, extracts sourced terms and proposes three growth hypotheses using search and model tools. It asks a human to confirm competitors and approve the final brief before export. The proposed success criterion is a useful, source-traceable brief within 15 minutes on at least 8 of 10 evaluated tasks, with no invented financial terms accepted during human review. That is an evaluation target, not a measured result.

## User and business problem

Growth teams need to understand how competing checking products are positioned, which conditions affect fees, and where a clearer switching journey or message might improve acquisition. Public information is scattered, changes over time and is easy to misread. Opening deposits, ongoing balances and fee-waiver balances are different concepts. Missing offer information should not be interpreted as the absence of an offer.

## Scope and deliverable

One home institution, one market, consumer checking accounts and three confirmed competitors. The output is a comparison of fees, opening funding, balance requirements, fee waivers, acquisition offers, eligibility, positioning and recent news, plus three proposed growth experiments. Fields lacking evidence remain Not verified. Each supported fact retains a source ID and supporting excerpt. Reports can be downloaded as Markdown and structured evidence JSON after approval.

## Architecture and agent roles

The Streamlit interface drives a LangGraph StateGraph. Discovery uses search evidence to propose competitors. The research agent searches each confirmed official domain and extracts one mainstream checking product per institution. It chooses a targeted follow-up query when the evidence is incomplete; the orchestrator permits at most one follow-up per institution. The analysis agent proposes evidence-linked hypotheses, an experiment, a success measure and a limitation for each. The orchestrator controls sequence, state, budgets, errors and native human interrupts.

Workflow: discovery → human confirmation → search → extraction/evidence check → bounded follow-up or next institution → analysis → human review → approved export or rejection.

This is a multi-agent orchestration pattern with specialized prompts and shared state. Agents do not conduct free-form conversations with one another. In live mode the model chooses competitor candidates, extracted fields and useful follow-up queries. In recorded mode those choices are curated fixtures; the graph, evidence checks, retries and approval gates still execute.

## Tools and data

Live mode uses Tavily search and a configurable OpenAI-compatible chat model through langchain-openai. Model name, endpoint and keys are configured locally. Development was tested with Python 3.12, Streamlit 1.65.0 and LangGraph 1.2.16.

Recorded sources collected October 24, 2026:

- Truliant: https://www.truliantfcu.org/bank/checking-comparison
- Truist: https://www.truist.com/checking
- Bank of America: https://www.bankofamerica.com/deposits/checking/advantage-banking/
- Skyla: https://www.skylacu.com/bank/checking/simply-checking

The demo dataset consists of short, noncontiguous official-page excerpts and curated extractions; it is not a stored Tavily response and does not contain complete disclosures. Acquisition offers, some membership requirements, recent news and other fields are intentionally left unverified. There is no private customer, transaction or internal bank data.

## State and memory

The graph stores request, candidates, confirmed competitors, source register, extracted facts, gaps, research index and round, hypotheses, warnings, trace and approval. InMemorySaver holds checkpoints across Streamlit reruns within the active session. Process restart or browser-session loss clears runs. There is no long-term memory claim; approved exports provide a retained artifact.

## Autonomy, human intervention and limits

Read-only research proceeds autonomously after competitor confirmation. One native interrupt pauses before research; another pauses before export. Rejection ends the run without downloads. The app does not send emails, publish campaigns, change product terms or write to a CRM. Internal ephemeral checkpoints are automatic; exporting a shareable report requires approval.

At most two search rounds per institution, five returned sources per search and two attempts per remote operation. For a complete run that is at most ten logical searches and thirteen logical model operations, each with one retry. Timeouts are configured per provider call. Total duration depends on provider latency; no measured live runtime is claimed yet.

## Evidence and error handling

A supported fact must reference a collected source on the confirmed official domain, include an exact whitespace-normalized excerpt match, and contain no numeric token absent from that quote. Explicit uncertainty is rejected, and all comparison terms are withheld when the selected product cannot be identified from source evidence. Live search requests fuller page text with a snippet fallback, capped at 14,000 characters per source. These checks catch source and amount fabrication but do not establish semantic truth or completeness. Source-supported means supported by the collected evidence, not independently verified. Full source review is a human responsibility.

Search or extraction failures are retried once; after that the system retains partial evidence and marks unsupported fields Not verified. Analysis failures retain the comparison and flag missing hypotheses. Live mode never silently falls back to curated demo answers. API errors are sanitized so provider response bodies and credentials are not exposed in the UI or trace. Collected text is treated as data in model prompts; prompt injection remains a limitation, and the system has no external write tools.

## Prompts used during AI-assisted development

The initial project-selection request was: “given that i work on FI space supporting the growth of banks and CUs Which project should I choose if I want to finish and submit it by tomorrow?”

The build request was: “Let's go with Project A. Help me build the Bank & Credit Union Growth Intelligence Agent and get it ready to submit by tomorrow.”

The implementation direction was: “Yes, proceed with Python + LangGraph + Streamlit. Pick a representative bank or credit union and market for the demo, and keep the scope focused so we can submit tomorrow.”

These are the actual development instructions, not invented iterations. Codex assisted with design, test writing, implementation and documentation. Runtime agent prompts are in growth/providers.py: they require structured JSON, one checking product per institution, source IDs and exact quotes, preservation of qualifiers, distinct balance concepts, and no invented claims. The analysis prompt labels proposed growth opportunities as hypotheses.

## Iterations and observations

1. Narrowed a broad FI growth assistant to checking-account competitor research to avoid internal integrations and meet the deadline.
2. Separated source-backed facts from growth hypotheses so experiments are not mistaken for proven outcomes.
3. Checked current official pages rather than assuming older “free checking” descriptions still apply; Truliant's current comparison presents Essentials Plus.
4. Added a recorded-evidence mode to demonstrate the graph and approval gates without credentials, while keeping that mode distinct from a live model run.
5. Added source-domain, quote and numeric consistency checks, bounded retries, explicit unknowns and a simulated outage.
6. Added automated graph and Streamlit interaction checks. See docs/verification.md for final observed results; do not claim live provider success until the live smoke check has passed.
7. Refined the interface after user feedback: navy research sidebar, blue-gray workspace, teal actions, compact summary cards, clearer comparison and opportunity sections, and expandable caveats.

## Evaluation approach

Automated checks exercise the graph end to end, approval and rejection, export gating, unknowns after an outage, retry bounds, domain lookalikes and invalid evidence. Streamlit AppTest checks the actual user interactions. These are software checks, not a benchmark of research quality or acquisition uplift.

Before submission, perform one live research run with configured credentials and inspect each supported term against its official page. Record the model/endpoint used, elapsed time, completeness, incorrect claims and whether the final brief was useful. A larger evaluation would use ten institution/market tasks scored against an independently assembled reference set. Growth hypotheses would need real experiments to establish business impact.

## Limitations and next steps

Search snippets can omit conditions, contain stale terms or mix products. Quote checks are lexical. Domain identity and market relevance require human confirmation. Membership eligibility and acquisition offers require full disclosure review. There is no persistent database, historical monitoring, campaign execution, verified market-share ranking or claim of production readiness. Next steps would be fuller source retrieval, independent evaluation, durable storage and testing with growth professionals.

## Submission links to add after final user actions

- GitHub repository: pending authenticated publication.
- Demo recording: pending user recording, maximum five minutes.
- Live provider verification: OpenAI and Tavily authenticated; a preliminary live run completed and prompted stricter source checks. See docs/verification.md for final QA results.

The handout's provided solution documents were not consulted during this implementation. The user should review the app and narrative, add their own live-run observations, and ensure the recording accurately represents which mode is demonstrated.


### Four-agent release update

Current workflow: Discovery → human competitor confirmation → Research → Strategy draft → Benchmarks → Strategy critique → one revision → human approval/export. Only checking and direct mail/display/paid social are supported. The original architecture above records the initial baseline; README and docs/verification.md describe the current release. Activity/cost tracking uses provider response metadata, not fabricated token counts. Costs are separate input/output estimates with dated model pricing, cache-read handling and explicit unknowns. Search credits are tracked separately. No LangSmith service is enabled. Editable all-in proposal scenarios are now available; internal benchmarks/rate cards and optimized forecasts remain future increments.


## Discovery to proposal checkpoint

Live workflow: competitor confirmation → institution research → strategist discovery checkpoint → ready: campaign draft, benchmark research, critique and one revision; incomplete: focused discovery questions with no campaign/benchmark/model calls → final human review/export. Refining the discovery brief reuses completed research. The four logical roles are unchanged. The default recorded replay retains its curated scenario; its optional checkpoint demonstrates readiness logic with zero external calls. Missing or explicitly unknown goal, timeframe, problem, observation, success definition or confirmation withholds campaigns. Client-reported inputs remain separate from source-supported public claims.


## Funded checking proposal scenarios

The Proposal planner uses strategist-provided all-in CPA assumptions (USD 300/450/600) and an explicitly entered funded-account target. Suggested channel envelopes are 70/30 direct mail/display and 60/25/15 when paid social is selected. Values are editable; the numerical split is a heuristic, not a verified industry benchmark. Exact-cent allocation reconciles to the total. No included costs are added again and no channel account-contribution forecast is inferred. Save before approval; unsaved edits block approval, approved/rejected values are locked, and saved inputs/totals are retained in gated Markdown and JSON exports. The calculator makes no provider calls. It does not rank a preferred campaign or automatically adopt public CPA candidates.
