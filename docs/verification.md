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

At the last credential check, neither Tavily nor model credentials was configured in the project .env or process environment. A live remote run has **not** been verified. GitHub CLI's saved authentication was expired at the last check; no repository has been published. The user requested keeping documentation local rather than publishing it to Drive.

## Remaining acceptance checks

Configure credentials, complete one live run, manually inspect official source terms, record the model and elapsed time, review the final narrative, publish the repository with intended access, record a five-minute-or-less demo and submit the form. Software checks are not a research-quality benchmark or evidence of business uplift.
