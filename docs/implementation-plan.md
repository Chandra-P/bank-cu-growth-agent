# Growth Intelligence Agent Implementation Plan

> For agentic workers: execute inline using executing-plans, with test-driven development and verification-before-completion. User authorized proceeding; do not add another approval checkpoint.

**Goal:** Deliver a focused Project A app and submission package.
**Architecture:** Pydantic evidence models, interchangeable live and recorded providers, a LangGraph orchestrator with two native interrupts, Streamlit interface and Markdown/JSON exports.
**Tech stack:** Python 3.12, Streamlit 1.65, LangGraph 1.2, langchain-openai, httpx, unittest.
**Spec:** docs/design.md

## Global constraints
- Public sources; checking accounts; home institution plus exactly three distinct competitors.
- At most two searches per institution and one retry per remote operation.
- No unapproved report export. No secrets in graph state or logs.
- Recorded replay is labeled and never called a live evaluation.

## Review focus
- Invented source IDs, mismatched domains, numbers absent from quotes: discard the claim.
- A permanent search outage: complete a partial report with explicit unknowns.
- Rejected or stale approval: no export from another run.
- Missing keys, invalid provider response, API failures: actionable sanitized errors.
- Streamlit reruns: retain the run and approval gate in the same session.

## Task 1 — evidence and provider contracts
Files: growth/models.py, growth/evidence.py, growth/providers.py, data/demo.json, tests/test_evidence.py, tests/test_providers.py.
- [x] Write failing tests for source validation, unknowns, distinct competitor domains, retry bounds, malformed API response handling and secret redaction.
- [x] Run unittest and observe missing behavior; implement validated models, bounded calls and providers.
- [x] Run the task suite to green.

## Task 2 — orchestrated research and exports
Files: growth/graph.py, growth/report.py, tests/test_workflow.py.
Interfaces: build_graph(search, analyst) returns compiled StateGraph; new_state(request) supplies serializable state; export_bundle(state) returns approved Markdown and JSON bytes.
- [x] Write failing end-to-end tests for confirmation, evidence collection, follow-up search, approval/rejection, permanent outage and export gating.
- [x] Implement discovery, research, analysis, interrupt gates, conditional follow-up and source-linked reports.
- [x] Run all tests to green and generate the recorded sample report.

## Task 3 — app and submission package
Files: app.py, .streamlit/config.toml, README.md, .env.example, requirements.txt, tests/test_app.py, docs/project-documentation.md, docs/demo-script.md, docs/submission-checklist.md.
- [x] Write failing Streamlit AppTest smoke/workflow tests.
- [x] Implement the app, instructions and truthful submission documentation.
- [x] Verify UI and graph suite; review the whole implementation for unsupported claims, secrets and gate bypasses.
- [x] Package a clean ZIP without credentials, caches or virtual environments; record verification results.
