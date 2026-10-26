# Ten FI recommendation evaluation

Evaluation date: October 26 2026. Synthetic client briefs; fresh public research; no client or campaign approvals.

**Result:** 10/10 automated rubric passes; mean final score 91.67/100 across all cases (unscored failures count as zero). Draft mean: 75.41/100.

Paired results: 9 improved, 0 declined, 1 unchanged among 10 scored pairs.

## Method

Recommendation component evaluation of all 10 fixed FI cases, reusing fresh baseline live research and production analyze/critique/revise prompts and citation gates; evaluation-only 120s timeout, 8000 completion tokens and low reasoning effort versus production 35s, 3800 tokens and provider default reasoning; chronology-blinded paired same-model judge. No actual client approvals.

Each dimension is scored 0–4: goal fit, evidence fidelity, channel fit, testability, measurement and safeguards. Pass requires ≥75/100, every dimension ≥2, no critical flag and valid structural gates. The judge sees chronology-blinded A/B versions. All ten fixed cases were included; failed cases remain in the denominator. Preliminary diagnostic runs are retained separately.

These scores assess the recommendation set, not automatic competitor ranking, website lookup, bank eligibility, public benchmark coverage or budget accuracy. Fixed FI domains and comparison sets are evaluation inputs.

## Case results

| Case | Institution and market | Problem | Draft | Final | Pass | Supported fields |
| --- | --- | --- | ---: | ---: | --- | ---: |
| FI01 | Frost Bank, San Antonio, Texas | Account funding | 83.33 | 95.83 | Yes | 15/36 |
| FI02 | United Heritage Credit Union, Austin, Texas | Application completion | 70.83 | 91.67 | Yes | 10/36 |
| FI03 | Truliant Federal Credit Union, Charlotte, North Carolina | Awareness | 83.33 | 91.67 | Yes | 14/36 |
| FI04 | BECU, Seattle, Washington | Account activation | 79.17 | 95.83 | Yes | 16/36 |
| FI05 | Digital Federal Credit Union, Worcester, Massachusetts | Account funding | 75.0 | 75.0 | Yes | 11/36 |
| FI06 | Alliant Credit Union, Chicago, Illinois | Awareness | 70.83 | 91.67 | Yes | 16/36 |
| FI07 | Huntington Bank, Columbus, Ohio | Application completion | 70.83 | 95.83 | Yes | 15/36 |
| FI08 | Regions Bank, Birmingham, Alabama | Account funding | 66.67 | 79.17 | Yes | 7/36 |
| FI09 | Fifth Third Bank, Cincinnati, Ohio | Account activation | 70.83 | 100.0 | Yes | 14/36 |
| FI10 | PNC, Pittsburgh, Pennsylvania | Application completion | 83.33 | 100.0 | Yes | 12/36 |

## Findings

Evidence coverage: 130/360 supported fields. A quality score must not be interpreted as complete competitor evidence.

### FI01 Frost Bank

Strength: Provides a disciplined, conditional testing plan across all three channels and carefully separates the synthetic target from any forecast or proven intervention.

Gap: The channel concepts are still similar in their reliance on funding-step messaging, and the plan does not establish that any channel can reach or measure the proposed audience.

### FI02 United Heritage Credit Union

Strength: Most complete on translating the synthetic goal into conditional tests and defining measurement and launch prerequisites without treating unknowns as facts.

Gap: The three interventions still rely on generic prompts, and the required audience, diagnosed friction, and operational details remain validation questions rather than established test inputs.

### FI03 Truliant Federal Credit Union

Strength: Carefully connects the scenario premise to a defined account outcome and makes evidence gaps, channel access, and measurement prerequisites explicit across all three concepts.

Gap: The three channel hypotheses have similar, generic interventions and do not establish that any channel is a meaningfully distinct or effective awareness treatment.

### FI04 BECU

Strength: The set makes the synthetic target and uncertainty explicit, defines the account-level activation outcome, and gives the three channels more distinct conditional intervention roles.

Gap: Channel access and customer friction remain unverified, so the concepts are test proposals rather than established channel recommendations; baseline evidence is also still needed.

### FI05 Digital Federal Credit Union

Strength: Careful evidence handling and strong safeguards; it retains the precise funded-account success definition and makes clear that the cause and outreach suitability are unverified.

Gap: The three channel concepts are mostly the same conditional reminder, with little channel-specific intervention or actionable experimental design.

### FI06 Alliant Credit Union

Strength: Consistently connects all three channel hypotheses to the synthetic goal and defined funded-account outcome while making evidence and launch dependencies explicit.

Gap: The three interventions are mostly channel substitutions; audience feasibility, survey validation, and operational test design remain unresolved.

### FI07 Huntington Bank

Strength: The set rigorously treats the scenario as synthetic, makes channel use conditional, and gives unusually clear validation, measurement, and spend gates.

Gap: Direct mail is deferred rather than developed as an actionable intervention, so the set offers fewer fully distinct, test-ready channel concepts.

### FI08 Regions Bank

Strength: Strong discipline about uncertainty and authorization, with a consistent funded-account outcome and explicit prerequisites across all three concepts.

Gap: The three concepts are repetitive prompt tests rather than meaningfully differentiated interventions, and channel-specific feasibility and measurement remain unresolved.

### FI09 Fifth Third Bank

Strength: The set consistently distinguishes the synthetic premise from verified facts and provides three conditional, differentiated tests with robust outcome measurement.

Gap: The recommendations appropriately defer launch pending validation; no material gap across the three concepts.

### FI10 PNC

Strength: The three concepts are differentiated, conditional on validating the actual barrier, and unusually explicit about measurement and operational prerequisites.

Gap: The proposals remain contingent and do not specify a concrete test design, which is appropriate given the unknown audience, permissions, budget, and funnel evidence.

## Usage

Production: 30 model attempts, 0 search attempts; 135,102 input and 46,207 output tokens; estimated model subtotal $0.039989.

Scoring: 10 model attempts; 71,456 input and 8,200 output tokens; estimated subtotal $0.013031.

Production unknown usage / unpriced calls: 0 / 0. Judge unknown usage / unpriced calls: 0 / 0. Tavily credits are separate; API attempts include retries.

## Limitations

This is a controlled component evaluation, not a production reliability pass. Same-model bias; one run per case; synthetic goals and fixed comparison sets. It does not establish human acceptance, campaign outcomes or the 60-minute productivity target.

Human strategist acceptance, the under-60-minute target and campaign acquisition outcomes have not been established. One same-model judge invocation per pair is susceptible to model and position bias, despite blinded chronology. A domain-expert review and repeated runs remain necessary.

## Reproduction

See evals/README.md and evals/run_live.py in the repository. The local result folder retains manifest.json, summary.json, scores.csv and ten evidence/result pairs. Frozen case and rubric hashes identify the protocol.
