# Strategist brief implementation plan

**Goal:** Turn the existing checking comparison into a client-needs-led discussion brief with a strategist takeaway and three sharper campaign concepts, then update the public app.

**Architecture:** Retain Python/LangGraph/Streamlit, the three logical agents and BYOK sessions. Add optional business-level client context to ResearchRequest, structured takeaway and campaign fields to the existing analysis response, and source-ID checks to the graph. No extra API operation is required. Keep legacy list responses readable for existing test doubles and old sessions; absent new fields render as questions/unknowns rather than invented details.

**Spec:** User authorized strategist takeaway and sharper campaign cards, checking only, direct mail/display/paid social only, and public deployment. Latest clarification: strategists gather client needs, annual goals or problems first, then propose appropriate solutions.

**UI:** Optional client discussion brief during setup. Before the comparison, show client context, strongest finding, strategic implication and a client validation question. Campaign cards show proposed audience, client-need connection, message, allowed channel rationale, test, outcome metric, guardrail and client question. Label research as evidence and all campaign proposals as hypotheses; recorded demo uses curated examples and never claims personalized model reasoning.

**Files:** growth/models.py (bounded fields and allowed-channel enum); providers.py (same-call analysis); graph.py (state and source validation); demo.py (curated examples); app.py (input/takeaway/cards); report.py (matching Markdown/JSON exports); tests/test_workflow.py and test_app.py (behavior/regressions).

- [x] Add failing tests for structured brief/export, permitted channels, client-context preservation and unsupported takeaway rejection.
- [x] Implement models, graph, live prompt and curated demo output.
- [x] Implement native UI and report export; keep approval and credential isolation.
- [x] Run tests and browser QA; fresh review for this revision; fix findings.
- [x] Commit/push verified changes to submission; verify hosted revision, regenerate credential-free submission ZIP.

Ruling: work in the existing dedicated project checkout, which is clean and has a known deployed commit. Only publish after tests and review. Do not add four-product support, branch scraping, vendor names, new data integrations, audience files or campaign activation.

Completed as part of the four-agent release; deployment verification is recorded in docs/verification.md.
