# Proposal planning implementation plan

**Goal:** Provide editable, deterministic funded-checking proposal scenarios using strategist-provided all-in CPA assumptions.

**Accepted defaults:** target entered by strategist (500 demo default); low/base/high CPA USD 300/450/600; all costs already included. Direct mail/display 70/30; selecting paid social resets suggested mix to 60/25/15. Mix is a planning heuristic, not a published benchmark or an account contribution forecast.

**Architecture:** growth/planning.py owns validated input, exact-cent arithmetic and native UI. A proposal state field is updated only while awaiting final review and only after discovery is ready (or explicitly curated recorded scenario). Saving preserves the review interrupt and clears approval acknowledgements; approved/rejected scenarios are locked. Client/discovery reset clears the scenario. Markdown and JSON exports retain the saved assumption provenance and budget envelopes under the existing approval gate. No new agents or API calls.

- [x] Observe failing tests for exact budgets, editable mix, validation, rounding, preserved approval interrupt/export and discovery gating.
- [x] Implement planner, state and exports; native Proposal planner tab, selected concept and target/CPA/mix overrides, explicit all-in/heuristic labels.
- [x] Test save versus unsaved edits, paid-social toggle, invalid allocations, reset/locking and final export.
- [x] Run full regression, independent review and browser check; publish and verify clean startup. Refresh secret-free ZIP.

**Non-goals:** channel-specific CPA, per-channel account forecasts, optimized allocation, spend execution, synthetic historical benchmarks, automatic preferred-campaign ranking, adding costs a second time.

Validation: 79 full-suite tests passed; independent review found no important defect. Browser confirmed paid-social defaults, exact expected totals and saved-scenario persistence before approval. Deployment verification is in docs/verification.md.
