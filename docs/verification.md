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

The public revision no longer loads saved credentials: each visitor must enter their own keys. GitHub CLI authentication remains expired and Streamlit Cloud is signed out, so no public deployment is claimed. Documentation remains local as requested.

## Remaining acceptance checks

Configure credentials, complete one live run, manually inspect official source terms, record the model and elapsed time, review the final narrative, publish the repository with intended access, record a five-minute-or-less demo and submit the form. Software checks are not a research-quality benchmark or evidence of business uplift.

## Visual redesign verification

The requested navy sidebar, blue-gray workspace and teal accents were implemented through native Streamlit themes, bordered cards, badges and compact typography. Comparison, opportunity and review sections use distinct containers. The four summary cards remain in a compact row in the narrow app preview, while the sidebar collapses automatically on small screens.

After the final redesign changes, the full suite passed again: **19 tests in 6.739 seconds**. Browser inspection confirmed the navy research panel, compact metrics, dark comparison header, opportunity cards and review state. Built-in pre-approval CSV export controls remained absent (browser count: zero). No live provider calls or credential changes were performed.

## Option 3 and visitor credentials — October 24, 2026

Implemented selected Modern Fintech concept with native Streamlit theme/layout, Inter typography, cobalt actions, blue-gray background, navy sidebar and three opportunity cards. Regression tests first failed because visitor inputs did not exist, then passed after implementation. Full suite: **26 tests passed in 9.804 seconds**; no cleanup exception in that run. Tests cover no environment credential fallback, both-key readiness, isolated browser-session inputs, clearing graph/config/results with keys, recorded workflow, approval gates and provider grounding/retries. No additional paid live call was made for the visual/public revision.

A code review found no blocking credential-isolation issues. A mode-aware landing copy issue was corrected. Browser QA exercised the key-free recorded workflow to final review with approval unchecked. Container deployment files are prepared; the Docker image has not been built in this environment. Account sign-in remains necessary before publication.
