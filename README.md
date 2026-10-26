# Bank and Credit Union Growth Intelligence Agent

A strategist workspace for consumer checking research and campaign proposals. Compare a client FI with three confirmed competitors, connect public evidence to client needs, review campaign concepts and save an acquisition budget before approving report downloads.

[Public app](https://bank-cu-growth-intelligence.streamlit.app/) · [Project documentation](docs/project-documentation.md) · [Evaluation method](evals/README.md)

## Run locally

Python 3.12 is the tested runtime.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\run.ps1
```

Enter local credentials in `.env`, never in source code. `run.ps1` launches `local_app.py` on loopback and can use saved OpenAI and Tavily keys automatically. To run the visitor-key interface instead:

```powershell
python -m streamlit run app.py
```

The recorded Charlotte demo needs no credentials. It uses curated evidence and outputs, not new model calls. Choose **Recorded evidence demo** and **Explore recorded demo**, confirm competitors, inspect results and acknowledge review to enable approval. The optional discovery checkpoint and simulated outage demonstrate controlled decision paths.

## Workflow

1. Enter an FI name and market; confirm the official website suggestion or correct it.
2. Review the three proposed competitor names and domains.
3. Research one checking product per FI and inspect source-supported terms and missing evidence.
4. Confirm the client goal, observed problem, timeframe and success definition. Missing discovery yields questions and no campaigns.
5. Generate three campaign concepts, research public CPA evidence, critique and revise once.
6. Save a target and budget scenario, review evidence and target alignment, then approve Markdown and JSON downloads.

The four logical roles are Discovery, Research, Strategy and Benchmarks. LangGraph orchestrates Python-controlled API calls and human interrupts; the model does not execute arbitrary tools. The app never launches campaigns, sends reports or commits spend.

![System architecture](docs/images/system-architecture.png)

![Agent workflow](docs/images/agent-workflow.png)

## Evidence and budget rules

Claims require a collected official-domain source, exact normalized quote and matching numeric terms. Missing information remains **Not verified**. This establishes traceability, not independent truth or complete disclosure review.

The default all-in checking CPA range of **$300/$450/$600** is a strategist assumption, not a verified benchmark. Mail/display defaults to **70/30**; including paid social suggests **60/25/15**. Shares are editable heuristics. All-in costs are not added again. Numeric targets and account outcomes must align before approval and export.

## Credentials and privacy

Public deployment uses **app.py**, which does not load local `.env`, process API keys or Streamlit secrets. Each visitor supplies their own keys for live research. Local saved-key access is isolated in `local_app.py` and requires loopback binding. `.env` and secret files are ignored and excluded from packages.

Keys reach the server for API calls and remain in visitor session memory. They are not intentionally written to reports, URLs or logs. **Clear keys & session** discards the active run and provider references. Closing a tab does not guarantee immediate memory cleanup.

## Tests and evaluation

```powershell
python -m unittest discover -s tests -v
```

The suite covers evidence grounding, retries, state resets, credential isolation, discovery and approval gates, budget arithmetic and usage accounting. Scored recommendation evaluation is opt-in and uses paid APIs; see [evals](evals/README.md). Automated rubric scores do not establish human acceptance, acquisition lift or the proposed under-60-minute productivity target.

## Repository structure

```text
app.py                Public Streamlit entry point
local_app.py          Loopback launcher with optional saved credentials
growth/               Workflow, providers, evidence, planning, reports and UI
data/                 Recorded demo fixture
tests/                Automated regression tests
evals/                Fixed cases, scoring rubric, runners and results
samples/              Labeled recorded demo and outage exports
docs/                 Project documentation, diagrams, deployment and demo guide
```

See [deployment](docs/public-deployment.md), [verification](docs/verification.md), [cost accounting](docs/cache-costs.md) and the [demo guide](docs/demo-script.md).
