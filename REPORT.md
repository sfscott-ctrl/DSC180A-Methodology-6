# Bikeshare demand: work through Part 5, Exercise 2

Scope: the supplied tutorial pipeline, Part 4 self-audit, and Part 5
Exercises 1–2. Exercises 3–5 are outside the requested scope. This is a
partial assignment, with actual code, results, fault evidence, and Git history.

## Results

The supplied mirror contains 728 daily observations, from 2011-01-03 through
2012-12-31. Calendar reindexing inserts the missing 2011-03-10 before any
shifting. The seven-day warmup and the gap remove 14 observed rows, leaving
348 training days in 2011, 182 validation days in H1 2012, and 184 test days
in H2 2012. Training preprocessing is fit only on training rows.

The proposed feature is `cnt_roll_3(d) = (cnt(d-1) + cnt(d-2) + cnt(d-3))/3`.
All its inputs are completed past days. It is built after calendar reindexing
with `.shift(1).rolling(3).mean()`. It requires no increase to the existing
seven-day warmup and changes the feature count from 14 to 15 without changing
the evaluation rows. The named-date test for 2011-02-17 checks
`(2115 + 1815 + 1913)/3 = 1947.6667`; it was committed while the feature was
still missing. A second test changes present/future counts and checks that
the feature at the prediction date stays unchanged.

| Feature set | Model | Validation R² | Validation MAE | Test R² | Test MAE |
|---|---|---:|---:|---:|---:|
| Before | baseline_mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Before | baseline_persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Before | ridge | 0.6475 | 832.9 | 0.5833 | 947.1 |
| Before | hgb | 0.2185 | 1296.6 | -0.4975 | 1972.6 |
| After | baseline_mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| After | baseline_persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| After | ridge | 0.6439 | 836.5 | 0.5800 | 946.2 |
| After | hgb | 0.1983 | 1311.6 | -0.5338 | 1998.7 |

MAE is measured in rides/day. Before rows match `reports/metrics_before.json`;
after rows match `reports/metrics.json`, including trailing-zero formatting.
`make all` regenerates both. The models and their hyperparameters were kept
unchanged: mean baseline, yesterday's observed count, standardized ridge with
alpha 1, and histogram gradient boosting with 300 iterations and seed 0.

On validation, the new feature changes ridge R² by **−0.0036** and MAE by
**+3.6**, and boosting R² by **−0.0202** and MAE by **+15.0**. Both are worse.
The skill therefore recommends dropping it. The feature is retained in the
submitted experimental pipeline to make this negative result reproducible;
it is not recommended for deployment. This decision was saved and committed
before the final test comparison. No alternative features or hyperparameters
were searched after seeing these outcomes.

The initial unchanged starter test suite did evaluate a test-set performance
threshold. That test was then moved to validation. No displayed test score
informed feature selection. Final before/after evaluation happened after the
decision was frozen; later regeneration and audit runs verify reproducibility.
Thus this report does not claim the held-out data were literally accessed
only once. The intentionally invalid leakage demonstration also uses its own
random holdout and is not a candidate for model selection.

## Headline finding

The naive leakage demonstration scores R² **1.000000** because `casual +
registered` reconstructs `cnt`; it predicts no unknown demand. Under the
chronological evaluation, the training-mean baseline has test R² **−2.1441**,
while persistence reaches **0.5099**. The extended ridge model reaches
**0.5800**, only **0.0701** above persistence, and loses on MAE (**946.2** versus
**840.1**). Boosting scores **−0.5338** yet still beats the mean baseline.
The new feature reduces validation performance for both models, so retaining
it documents a failed experiment, not a predictive improvement.

The training maximum is 6,043 rides; 56.5% of test days exceed it, and the
test maximum is 8,714. Boosting predicts at most 5,625.3 on test, while ridge
reaches 7,490.0.
The range evidence and standardized ridge coefficients are saved in
`reports/model_evidence.json`. Ridge can extrapolate through linear lag
coefficients; the booster's piecewise constant response does not continue
trends outside its learned input ranges. An additive boosted ensemble is
not universally bounded by the minimum and maximum training target, so the
empirical evidence is stronger than asserting an absolute range theorem.

These are retrospective results using observed same-day weather as a proxy
for weather forecasts. Daily realized weather is not available before the
day begins. A deployed day-ahead service would need forecast-vintage inputs
and a new evaluation. Persistence and lagged models also use each actual
previous day's count, so this is sequential daily evaluation, not a six-month
forecast issued in January.

Exercise 2 evidence is in `docs/SEEDED_FAULTS.md`: exact mutations, actual
red tests, hook stderr, restoration results, and repair-turn counts. The
unknown-weather test was added because the starter hook's leakage suite
otherwise lacked coverage for that mutation. Explicit raw-column
classification catches new columns independently of the numeric selector.
The fourth experiment uses a disposable copy to demonstrate why Edit/Write
permissions and hooks do not protect against a Bash `cp`.

The Part 4 self-audit reports no target leakage, valid temporal splitting,
both baselines present, and reproducible metrics. Its six findings and the
Codex assessment are preserved in `docs/SELF_AUDIT.md`. The observed-weather
limitation is accepted; a validation-artifact command gap was fixed with
`python -m scripts.reproduce_validation`. The remaining selector, warmup,
estimator-state, and historical-test-exposure caveats do not establish a
change to the printed numbers; they are addressed explicitly in that document.
The successful audit and the earlier timed-out attempt are both recorded.

## Exercise 4: target transformation

Not performed: this is beyond the requested stopping point of Exercise 2.
The committed pipeline uses the untransformed target.

## Exercise 5: ridge vs persistence

Not performed as a separate deployment argument: this is beyond the requested
scope. The measured comparison is reported above without claiming deployment
readiness.

## Attribution

Models used: NRP service `qwen3` through Claude Code 2.1.328 (the API returned
backend identifier `Qwen/Qwen3.8-Flash-Next-FP8`). The [NRP catalog](https://nrp.ai/llms/)
lists `qwen3` as 180B parameters, 6B active, with a 1M-token context.
GPT-6 in Codex handled orchestration, additional checks, analysis, and this
write-up. No local Ollama model was downloaded. Both agents were
used, rather than attributing the entire repository to one model.

Agent-generated or agent-modified work:

- NRP/Claude: `/new-feature` invocation, the named-date failing test,
  `cnt_roll_3`, its validation decision entry, and the live fault/repair runs.
- Codex: raw-column classification, weather and perturbation tests,
  validation-only evaluation and before/after export, NRP launch script,
  `/seed-fault` skill, fault evidence capture, raw-data integrity enforcement,
  model evidence, bounded SDK reviewer instructions, report, and staged Git history.
- The original pipeline, original tests, hook, reviewer, and Agent SDK auditor
  came from the course starter; the first commit preserves them unchanged.

Human instructions actually supplied:

- Complete the assignment through Part 5, Exercise 2.
- Use the supplied NRP access if needed.

The feature choice, negative-result retention, additional safeguards, and
interpretation were agent recommendations, documented as such in
`docs/DECISIONS.md`. This report does not invent student decisions or claim
that a human independently reviewed these findings. The student should
review and own the conclusions before submitting them. No teammate audit,
remote publication, or course submission is claimed.
