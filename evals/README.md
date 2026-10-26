# Recommendation evaluation

This opt-in evaluation uses ten fixed FI and market cases.
Goals and observations are synthetic, not actual FI performance or client instructions.
The cases cover awareness, application completion, funding and activation.
Official domains and competitor sets are fixed test inputs, not scored discovery outputs
or a claim that they are the market's top three competitors. Website lookup is outside
this evaluation's scope.

## Production reliability and recommendation quality

`run_live.py` runs the current production graph without model-setting overrides.
`run_quality.py` separately reuses its collected public evidence and evaluates the
production recommendation prompts and citation gates with an evaluation-only
120-second timeout, 8,000 completion-token budget and low reasoning effort. The
historical pre-fix baseline used 35 seconds, 3,800 completion tokens and provider-default
reasoning. The application now uses 120 seconds, 8,000 tokens and low reasoning.
Quality scores under the controlled configuration are not ten-case production
completion results. All ten cases use the same evaluation settings.

An initial 120-second diagnostic with the production token budget was stopped after
budget-exhaustion failures; its artifacts are retained locally and its results are
not substituted into the scored suite. The final suite reruns every fixed case,
not only failed or promising cases.

## Method

Fresh Tavily research and the production draft, benchmark, critique and revision steps
run for every case. The graph stops at final human review: no client approval,
export, activation or external business write is performed.

A separate model invocation receives two chronology-blinded recommendation versions
(A and B), the synthetic brief and the grounded profiles. It assesses the initial
draft and final output on six dimensions from 0 to 4:

| Dimension | Full credit requires |
| --- | --- |
| Goal fit | All concepts address the specified funnel problem and outcome |
| Evidence fidelity | Material assertions match grounded facts and qualifiers |
| Channel fit | Each channel has a credible role and explicit audience assumptions |
| Testability | Actionable intervention, audience, comparison and dependencies |
| Measurement | Defined account outcome, attribution window, deduplication and baseline or holdout |
| Safeguards | Explicit permissions, assumptions, disclosures and execution limits |

Common anchors: 0 absent or harmful; 1 major defects; 2 partially useful with material
gaps; 3 solid with minor gaps; 4 specific and complete across all three concepts.
The full frozen rubric and its SHA-256 hash are included in each run manifest.

Case score is the sum divided by 24, multiplied by 100. A pass requires at least
75/100, no dimension below 2, no critical flag, three campaigns, permitted channels
and source IDs contained in the grounded profiles. Critical flags require an exact
recommendation quote and a reason (material unsupported claim, fabricated benchmark,
guaranteed outcome or unsafe activation). Invalid judge output receives one bounded
retry. Cases without usable recommendations or valid scoring stay in the ten-case
denominator and contribute zero to the all-case mean.

The judge uses the same configured model as generation, in a separate invocation;
this is not independent expert validation. Same-model bias, non-determinism, a small
fixed convenience sample and one run per case limit generalization. It does not
prove human acceptance, acquisition lift, or the under-60-minute productivity target.
Scores concern the recommendation sets, not live public benchmark availability or
the correctness of a separately saved campaign budget.

## Reproduce

Run from the project directory with Python 3.12 and requirements installed. A local
`.env` must contain your OpenAI and Tavily credentials. Running this uses paid APIs.

```powershell
python -m unittest discover -s tests -p test_recommendation_evaluation.py
python -m evals.run_live --output C:/path/to/production-results --workers 2
python -m evals.run_quality --baseline C:/path/to/production-results --output C:/path/to/quality-results
```

Use a fresh output directory for each run. Output contains the frozen rubric and
case hash, case evidence, paired scores and explanations, warnings, usage and the
aggregate summary. Never put credentials into case inputs or result files.
Provider cost estimates and search credits are separate from quality scores.

The scored [quality results](results.md), [pre-fix production baseline](production-results.md)
and [post-fix production smoke](production-smoke.json) are reported separately. Raw public evidence is kept with the local run artifacts;
the repository includes compact scores and rubric explanations.
