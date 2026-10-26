# Ten FI recommendation evaluation

Evaluation date: October 26 2026. Synthetic client briefs; fresh public research; no client or campaign approvals.

**Result:** 2/10 automated rubric passes; mean final score 18.33/100 across all cases (unscored failures count as zero). Draft mean: 16.67/100.

Paired results: 1 improved, 0 declined, 1 unchanged among 2 scored pairs.

## Method

10 live production graph cases, synthetic confirmed briefs, fixed comparison inputs; paired A/B chronology blinded same-model judge; no human/client approvals or campaign execution

Each dimension is scored 0–4: goal fit, evidence fidelity, channel fit, testability, measurement and safeguards. Pass requires ≥75/100, every dimension ≥2, no critical flag and valid structural gates. The judge sees chronology-blinded A/B versions. All ten fixed cases were included; failed cases remain in the denominator. Preliminary diagnostic runs are retained separately.

These scores assess the recommendation set, not automatic competitor ranking, website lookup, bank eligibility, public benchmark coverage or budget accuracy. Fixed FI domains and comparison sets are evaluation inputs.

## Case results

| Case | Institution and market | Problem | Draft | Final | Pass | Supported fields |
| --- | --- | --- | ---: | ---: | --- | ---: |
| FI01 | Frost Bank, San Antonio, Texas | Account funding | Unscored | Unscored | No | 15/36 |
| FI02 | United Heritage Credit Union, Austin, Texas | Application completion | Unscored | Unscored | No | 10/36 |
| FI03 | Truliant Federal Credit Union, Charlotte, North Carolina | Awareness | Unscored | Unscored | No | 14/36 |
| FI04 | BECU, Seattle, Washington | Account activation | Unscored | Unscored | No | 16/36 |
| FI05 | Digital Federal Credit Union, Worcester, Massachusetts | Account funding | Unscored | Unscored | No | 11/36 |
| FI06 | Alliant Credit Union, Chicago, Illinois | Awareness | 75.0 | 91.67 | Yes | 16/36 |
| FI07 | Huntington Bank, Columbus, Ohio | Application completion | Unscored | Unscored | No | 15/36 |
| FI08 | Regions Bank, Birmingham, Alabama | Account funding | Unscored | Unscored | No | 7/36 |
| FI09 | Fifth Third Bank, Cincinnati, Ohio | Account activation | 91.67 | 91.67 | Yes | 14/36 |
| FI10 | PNC, Pittsburgh, Pennsylvania | Application completion | Unscored | Unscored | No | 12/36 |

## Findings

Evidence coverage: 130/360 supported fields. A quality score must not be interpreted as complete competitor evidence.

### FI01 Frost Bank

Strength: No valid judgment available.

Gap: Run or scoring failed: ValueError

### FI02 United Heritage Credit Union

Strength: No valid judgment available.

Gap: Run or scoring failed: ValueError

### FI03 Truliant Federal Credit Union

Strength: No valid judgment available.

Gap: Run or scoring failed: ValueError

### FI04 BECU

Strength: No valid judgment available.

Gap: Run or scoring failed: ValueError

### FI05 Digital Federal Credit Union

Strength: No valid judgment available.

Gap: Run or scoring failed: ValueError

### FI06 Alliant Credit Union

Strength: Thoroughly preserves the synthetic nature of the discovery and makes the three channel tests conditional, measurable, and subject to substantial validation.

Gap: The concepts are highly repetitive product-introduction tests rather than meaningfully distinct interventions.

### FI07 Huntington Bank

Strength: No valid judgment available.

Gap: Run or scoring failed: ValueError

### FI08 Regions Bank

Strength: No valid judgment available.

Gap: Run or scoring failed: ValueError

### FI09 Fifth Third Bank

Strength: Carefully ties all three tests to the specified activation outcome while acknowledging that the cause, rate, and reachable audiences are unknown.

Gap: The three interventions are variations on setup education, and the holdout assignment and overlap rules need operational definition.

### FI10 PNC

Strength: No valid judgment available.

Gap: Run or scoring failed: ValueError

## Usage

Production: 126 model attempts, 101 search attempts; 1,029,392 input and 137,152 output tokens; estimated model subtotal $0.191385.

Scoring: 2 model attempts; 13,866 input and 3,383 output tokens; estimated subtotal $0.003425.

Production unknown usage / unpriced calls: 19 / 19. Judge unknown usage / unpriced calls: 0 / 0. Tavily credits are separate; API attempts include retries.

## Limitations

Same model family for generator and judge; one run per case; not independent expert ratings, causal campaign effectiveness, domain-discovery accuracy or the 60 minute human productivity test.

Human strategist acceptance, the under-60-minute target and campaign acquisition outcomes have not been established. One same-model judge invocation per pair is susceptible to model and position bias, despite blinded chronology. A domain-expert review and repeated runs remain necessary.

## Reproduction

See evals/README.md and evals/run_live.py in the repository. The local result folder retains manifest.json, summary.json, scores.csv and ten evidence/result pairs. Frozen case and rubric hashes identify the protocol.
