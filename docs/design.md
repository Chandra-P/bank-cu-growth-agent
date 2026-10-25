# Bank & Credit Union Growth Intelligence Agent

Approved direction: Python, LangGraph and Streamlit; focused Project A submission by October 25, 2026. The user delegated demo institution and market selection and authorized implementation.

## Goal
Help a bank or credit union growth professional compare three competitors' checking products and review three evidence-linked growth hypotheses. Demo: Truliant Federal Credit Union, Charlotte, North Carolina. Public-source research only; no internal systems required.

## Approaches
Python + LangGraph + Streamlit was selected by the user for inspectable orchestration, tests and a portable GitHub submission. n8n was considered but would add integration setup uncertainty. A recorded-evidence demo complements live research and is always labeled; it never masquerades as a live model run.

## Workflow and boundaries
Discovery agent proposes three competitors from search evidence. Human confirms or edits names and official domains. Research agent searches those domains, extracts checking facts, and chooses at most one additional search per institution when evidence is incomplete. Strategy agent proposes three checking campaign concepts tied to client needs and grounded sources. A fourth Benchmarks agent researches public acquisition CPA evidence; Strategy then critiques and revises once, preserving the original draft and review findings. The LangGraph orchestrator checkpoints state, limits retries, records tool outcomes and pauses twice using native interrupts. Human approval is required before report download. Rejection ends the run without an export.

Compare home institution plus three competitors: product name, monthly maintenance fee, opening deposit, ongoing balance requirement, fee waivers, acquisition offers and conditions, membership eligibility, positioning and recent news. Unknown is not zero. Extracted facts must reference a collected official source and an exact supporting excerpt; numeric claims must be present in that excerpt. Evidence-backed means source-supported, not independently verified. Hypotheses remain explicitly labeled inference.

## Scope
One market and checking accounts only. Two search rounds per institution, up to five sources per round, one retry per remote operation, finite model response sizes. LangGraph in-memory checkpoints survive Streamlit reruns within the session; process restarts clear runs. Credentials are read from environment or local .env and are never placed in graph state, reports or logs. No sending, publishing, CRM integration, monitoring or customer data.

## Interface
Start with an offline recorded-evidence demo or configure live Tavily and OpenAI-compatible credentials. Confirm competitors, watch progress, inspect the brief/evidence/trace, then approve export. Offline replay accepts only its documented demo scope. Include a simulated search outage to demonstrate bounded recovery without fabricating findings.

## Deliverables and acceptance
Runnable app, reproducible dependencies, meaningful automated tests, recorded sample briefing for three competitors, local documentation plus a native Google Doc when connector access permits, demo script, submission checklist and ZIP. Verify the offline graph end to end including both approval gates, unavailable sources, source validation and Streamlit UI. Live-provider verification depends on user-configured credentials and must be reported separately. GitHub publication and recording/submission are final user-facing steps; do not claim they happened without evidence.


### Four-agent release update

Current workflow: Discovery → human competitor confirmation → Research → Strategy draft → Benchmarks → Strategy critique → one revision → human approval/export. Only checking and direct mail/display/paid social are supported. The original architecture above records the initial baseline; README and docs/verification.md describe the current release. Activity/cost tracking uses provider response metadata, not fabricated token counts. Costs are separate input/output estimates with dated model pricing, cache-read handling and explicit unknowns. Search credits are tracked separately. No LangSmith service is enabled. Campaign-budget calculation and internal benchmarks/rate cards are future increments.
