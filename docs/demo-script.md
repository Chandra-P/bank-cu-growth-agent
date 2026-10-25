# Five-minute demo recording script

Target 4 minutes 30 seconds. Record the application and your voice; keep credentials and .env files off screen. Rehearse once. Use a live run if credentials are ready; otherwise explicitly identify recorded mode and explain that live API evaluation is pending.

## 0:00–0:30 — User and problem

“I work with banks and credit unions on growth. I built a checking-account competitor research agent to turn scattered product pages into a sourced comparison and three growth hypotheses. The demo institution is Truliant in Charlotte.”

## 0:30–1:00 — Scope and architecture

Show the How it works tab after the brief is available, or explain the flow first: discovery, research, analysis and a LangGraph orchestrator. “It keeps state across steps and uses two human checkpoints. Each institution gets at most two searches, and failed remote calls get one retry.”

## 1:00–1:40 — Discovery and confirmation

Start a run. Show the three candidates and official domains. Explain why the comparison set needs human confirmation: local relevance and credit union membership restrictions. Click Confirm and research. If the live run takes too long, show an already completed live run and explain when it ran; do not present recorded data as freshly searched.

## 1:40–2:40 — Comparison and evidence

Show the checking comparison. Point out opening deposit versus ongoing balance and fee-waiver conditions. Open one institution in Evidence & gaps and show a supporting excerpt, source link and retrieval date. “Not verified is explicit missing evidence; it is not zero and does not prove no offer exists.”

## 2:40–3:20 — Growth hypotheses

Show one opportunity, its experiment and metric. “These are ideas to validate, not claims of guaranteed growth. The evidence supports the observed terms; the strategic interpretation still needs judgment.”

## 3:20–3:55 — Error recovery

If using the recorded outage demo, state clearly: “This second run is a recorded-evidence replay with an injected Skyla outage.” Show the trace's two failed attempts and the unknown Skyla fields. Explain that the remaining comparison still completes. You may pre-run the outage example in a second tab to stay within five minutes; never imply it is a live API outage.

## 3:55–4:20 — Human review and export

Show downloads are absent before approval. Add a caveat, acknowledge review, approve, then download the briefing and evidence JSON. Explain that rejection prevents export.

## 4:20–4:40 — AI tools, learning and limits

“I used Codex to help scope, code, test and document this build. The biggest lesson was that evidence, state and failure behavior matter as much as prompts. Quote checks are not semantic verification, and full disclosures still need review. The GitHub repository contains the app, tests and reproducible recorded sample.”

Replace any unperformed claim with what actually happened. Mention live provider validation only after an observed successful live run. Add your own learning from using the app.

## Updated four-agent demonstration

Enter a business-level client goal, run the recorded demo and confirm competitors. Explain that its outputs are curated, not personalized. Show the strategist takeaway and a campaign card with direct mail/display/paid social roles. Open Benchmarks: recorded CPA is unknown, not an invented public benchmark. Open Review & revision: show the three findings and original-versus-final guardrail. Open Agent activity & costs: recorded mode has zero external calls and no simulated token totals. In live mode the same panel shows real provider attempts, separate input/output tokens and estimated model costs, with unknowns explicit. Finish at the unapproved human checkpoint. No campaign is published.


## Discovery to proposal decision demo

Enable Explore the discovery checkpoint in the recorded setup, start research and confirm competitors. At the new checkpoint, inspect the research snapshot and continue with the problem unknown. Show the Discovery needed decision, focused questions and zero campaign concepts; campaign/benchmark/revision calls are skipped. Click Complete discovery without repeating research. Enter an explicitly illustrative client-reported goal, timeframe, application-completion barrier, supporting observation and measurable success definition, then confirm. Explain that the recorded concepts remain curated; a live run uses the structured diagnosis in Strategy prompts. Show Recommendation logic & measurement on a campaign, then review/revision, costs and final human approval. Distinguish client-reported problems from source-supported public terms. Do not claim that checkbox confirmation proves a diagnosis or that public competitor research identifies an internal funnel problem.
