# Verification

## Automated checks

94 unittest checks passed on October 26 2026, including scoring, model-budget and bounded evaluation-wait checks.
Coverage includes evidence grounding, provider retry bounds, preserved evidence after
outages, discovery readiness, client state resets, credential isolation, cache cost
arithmetic, proposal rounding, target alignment and approval/export gates.

The full suite uses Streamlit AppTest and must run in an environment that allows its
local runtime. The restricted sandbox stalled; the unrestricted local run passed.

```powershell
python -m unittest discover -s tests -v
```

## Ten-case evaluation

Quality component: **10/10 passes**, mean final score
**91.67/100**. See [quality report](../evals/results.md)
and [machine-readable scores](../evals/results.json).

Historical pre-fix production baseline: **2/10 rubric passes**;
2/10 cases produced valid paired scores. See the separate
[production report](../evals/production-results.md). Do not confuse component
scores with production reliability.

Quality runs reused fresh live evidence with 120-second model
timeouts, an 8,000-token completion budget and low reasoning effort. These settings
are now adopted by the application; the baseline used 35 seconds, 3,800 tokens and
provider-default reasoning. A fresh post-fix United Heritage end-to-end smoke passed
in 127.5 seconds with a 91.67/100 score. The full ten-case end-to-end run has not been
repeated after the fix. All fixed cases use
synthetic client goals. Generation and scoring use the same model family with
chronology-blinded A/B versions; no expert-human acceptance rating is claimed.

The initial diagnostic with a longer timeout and the original token budget did not
produce valid output in the first completed case and was stopped. Diagnostic
artifacts were preserved; none were substituted into the final ten-case suite.

## Recorded samples

Both recorded CLI samples were regenerated and exported successfully:

```powershell
python -m growth.cli --demo --approve-demo
python -m growth.cli --demo --approve-demo --outage
```

They are labeled curated replays and scripted demo approvals, not new live model
results or actual client approvals. The public app remains visitor-key-only.

## Limits

Passing regression checks does not establish live availability or campaign lift.
The pre-fix timeout/output failure is retained in the baseline; one post-fix smoke
is not a full production reliability study. Human
review of complete product terms, eligibility, audience access and the client
diagnosis is required. The proposed 60-minute / 8-of-10 strategist target remains
unmeasured.
