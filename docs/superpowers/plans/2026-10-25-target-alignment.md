# Target alignment and live rehearsal plan

**Goal:** Prevent approving a funded-checking budget against a different client target, then rehearse a fresh live run through saved budget and approved demo export.

**Design:** Add optional structured target count and outcome to client discovery, with zero/not specified meaning unknown. Planner defaults from a known funded-account target. Numeric mismatch or opened/activated target incompatibility blocks save, final approval and export. Missing numeric/outcome target remains explicitly a planning assumption and requires a separate target-review acknowledgement at approval, recorded in approval metadata. Never infer a count from free text. Reset acknowledgements on edits/saves and retain checks server-side.

- [x] Observe failing alignment tests; add fields, validation and clear comparison messages.
- [x] Update planner, graph approval and export guards; test matched, mismatched, unknown and incompatible targets including dirty edits.
- [x] Full regression and independent review; inspect target-alignment UI.
- [x] Fresh live illustrative Frost/San Antonio run: website, competitor review, structured 300-funded target, draft/review/revision, 300-account 60/25/15 budget, explicit automated demo approval, exported Markdown/JSON. Verify target, costs and evidence/limitations survive export; no real client approval or campaign execution.
- [x] Publish after checks; clean cloud restart; refresh ZIP and retain rehearsal artifacts without credentials.

Validation and rehearsal details: docs/verification.md. Live artifacts remain in the parent outputs folder, outside the published project.
