# Discovery to proposal implementation plan

**Goal:** Tie campaigns to a strategist-confirmed client problem; produce discovery questions when the diagnosis is incomplete.

**Architecture:** Add a structured ClientDiscovery model and native LangGraph interrupt after research, before Strategy. Live runs always pause; the explicitly labeled recorded fixture retains its curated checkpoint scenario for reproducibility. A recorded incomplete-discovery option exercises the new gate. Strategy's deterministic readiness check prevents campaign/model/benchmark work for an unknown problem. Preserve evidence and resume at this checkpoint when refining a discovery brief. Existing final approval still gates all exports.

**Files:** growth/models.py holds structured fields. growth/discovery.py owns readiness/questions and Streamlit form. growth/graph.py owns gate/routing and state. app.py renders decision, logic and resume. providers.py reinforces separation of client-reported facts/public evidence. report.py exports decisions/questions/context. tests/test_discovery.py verifies unknown, incomplete, ready, resume and no bypass.

- [x] Write failing graph tests for live interrupt, unknown problem withholding, confirmed ready brief, and checkpoint resume without new research.
- [x] Implement typed fields, deterministic readiness and questions, gate and conditional routing. Keep four logical roles.
- [x] Implement native checkpoint form, decision panel, problem-to-recommendation logic, explicit recorded labeling and export preservation.
- [x] Strengthen Strategy/review prompts; do not infer internal performance from public pages.
- [x] Run focused and full regressions; review security/gates; exercise recorded unknown and ready paths in browser. Publish only after checks pass and verify public startup.

**Acceptance:** Unknown barrier or missing goal/timeframe/observed evidence/success definition/confirmation means zero campaigns. No invented KPI, CPA, budget or internal bottleneck. Branch overlap, budget calculator and additional products remain deferred. Old memory-only sessions should start a fresh run for the new checkpoint.

Validation: 71 full-suite tests passed; two checkpoint UI tests passed after adding research inspection. Independent review found and verified fixes for canonical unknown-value readiness and unconfirmed export labeling. Browser and deployment verification are recorded in docs/verification.md.
