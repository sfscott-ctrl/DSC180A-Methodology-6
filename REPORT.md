# Bikeshare demand: methodology assignment

Required Exercises 1–5 are implemented and checked. The final SDK audit
refresh is pending NRP recovery; optional Exercise 6 was not attempted.
Repository: [DSC180A-Methodology-6](https://github.com/sfscott-ctrl/DSC180A-Methodology-6).
Nothing has been submitted to the course.

## Results

The supplied mirror has 728 observations, 2011-01-03 through 2012-12-31,
with 2011-03-10 missing. Restoring the daily calendar before lagging and
removing incomplete history leaves 714 rows: 348 training days in 2011,
182 validation days in H1 2012, and 184 test days in H2 2012. The first
seven observations and seven following the missing day account for the
14-row loss. Preprocessing is fit only on training rows.

The added feature is the mean of the three completed prior days:
`cnt_roll_3(d) = [cnt(d-1) + cnt(d-2) + cnt(d-3)] / 3`. It uses
`.shift(1).rolling(3).mean()` after calendar reindexing, changes 14 features
to 15, and leaves the original seven-day warmup and evaluation rows unchanged.
The test written and committed first checks 2011-02-17 against
`(2115 + 1815 + 1913)/3 = 1947.6667`. A perturbation test confirms that changing
current/future counts does not alter that day's feature.

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

MAE is rides/day. All eight rows match `reports/metrics.json`, including
`feature_comparison.before` and `.after`; its top-level scores use the added
feature. `make all` regenerates that file and `metrics_before.json` using
fixed settings and the starter's pinned dependencies.

On validation, the feature reduces ridge R² by 0.0036 and increases MAE by
3.6; it reduces HGB R² by 0.0202 and increases MAE by 15.0. The skill
recommends dropping it. It remains in the submitted experimental pipeline
to reproduce the negative finding, with `recommended_for_deployment=false`. This retention
was committed before the final comparison; it is not a claimed improvement.
The validation-only regeneration command is
`python -m scripts.reproduce_validation`.

## Headline finding

The leaky demonstration achieves R² 1.000000 because `casual + registered`
exactly reconstructs `cnt`. Chronological evaluation of the extended
untransformed model gives mean-baseline test R² −2.1441, persistence 0.5099,
ridge 0.5800, and HGB −0.5338. Ridge gains only 0.0701 R² over persistence
and loses on MAE, 946.2 versus 840.1. HGB is negative yet still beats the
mean baseline. The additional feature worsens validation and is retained
only as a documented experiment. A separate, validation-selected target
ratio lets HGB reach test R² 0.6225 and MAE 829.4; its MAE margin over
persistence is just 10.7 rides/day.

Training demand peaks at 6,043 rides; 56.5% of test days exceed that value,
and test peaks at 8,714. The untransformed HGB predicts at most 5,625.3;
ridge reaches 7,490.0. A piecewise constant tree response cannot continue
an input trend beyond learned split ranges. An additive boosted ensemble
is not universally bounded by the training-target range, so the empirical
ranges, rather than an absolute range theorem, support this explanation.
Standardized ridge coefficients and range evidence are in
`reports/model_evidence.json`.

All comparisons condition on observed daily weather. Those realized values
are not available before the day starts; deployment requires a new evaluation
with forecast-vintage weather. Lagged demand is updated with actual completed
days, so this is sequential one-day evaluation, not a six-month forecast
issued at one origin.

Exercise 2's actual test failures, automatic hook stderr, repair counts,
and raw-copy demonstration are in `docs/SEEDED_FAULTS.md`. The new hash
guard catches the Bash copy that the Edit/Write hook misses. Exercise 3's
teammate audit at commit `f7bf8c5` is in `docs/AUDIT.md`, with verbatim model
output and a separate Codex verdict. Its useful comparison concern is that
the teammate's transformed model has worse test MAE than persistence,
891.2 versus 840.1. Independent checks rebut several overreaching audit
claims; no incorrect current score was demonstrated. Our own SDK audit is
in `reports/audit.jsonl`, with findings assessed in `docs/SELF_AUDIT.md`.
The earlier audit found no target leakage and reproduced the scores. Its
weather and initial test-exposure concerns are accepted above and below.
Its validation-regeneration concern is resolved by the documented command,
whose outputs match exactly. Deny-by-name selection, warmup/lag coupling,
and mutable estimators are future-maintenance concerns; independent calendar
checks and fresh-process reproduction show no corresponding current score
error. These checks do not guarantee that arbitrary future features are safe.
Three attempts to refresh the SDK audit after Exercise 4 failed with NRP
HTTP 503/500/503 errors. The retained JSON is the successful earlier audit,
not a review of the transformation; final refresh is pending. Independent
fresh-checkout verification passed 25 tests and reproduced five result files
byte-for-byte (`reports/evidence/completed_assignment_checks.json`).

## Exercise 4: target transformation

Before running the study, commit `df68340` predeclared three transformations
and the selection rule. Every candidate uses the same 15 predictors, 348
training rows, and `HistGradientBoostingRegressor(random_state=0,
max_iter=300)`. Only the target formulation changes:

- `delta_lag1`: learn `cnt - cnt_lag_1`, then add yesterday's count.
- `delta_roll7`: learn `cnt - cnt_roll_7`, then add the previous seven-day mean.
- `ratio_roll7`: learn `cnt / cnt_roll_7`, then multiply by that historical mean.

The criterion was highest validation R², with lower MAE breaking a tie.
Predictions are not clipped. All scores below are in original ride units;
dashes mean the unselected candidate was not evaluated on test.

| Model / target | Validation R² | Validation MAE | Test R² | Test MAE |
|---|---:|---:|---:|---:|
| baseline_mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| baseline_persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| ridge | 0.6439 | 836.5 | 0.5800 | 946.2 |
| hgb | 0.1983 | 1311.6 | -0.5338 | 1998.7 |
| hgb delta_lag1 | 0.6251 | 805.4 | — | — |
| hgb delta_roll7 | 0.7209 | 722.4 | — | — |
| hgb ratio_roll7 | 0.7483 | 681.5 | 0.6225 | 829.4 |

`ratio_roll7` won validation by 0.1044 R² and 155.0 MAE relative to ridge.
Commit `7ed9227` froze that choice and the validation-file hash before its
single transformed-model test evaluation. The selected model then achieved
0.6225/829.4 on test, versus ridge 0.5800/946.2 and persistence 0.5099/840.1.
No choice changed afterward. Earlier untransformed test scores had already
been seen during the partial assignment; they cannot be unseen. This study
used validation only for selection and evaluated only its chosen transformed
model on test once. Later verification repeats validation and the canonical
untransformed pipeline, not a search over transformed test scores.

The transformation is defensible for sequential one-day prediction: the
scale is a positive mean of seven strictly earlier calendar days. It lets a
learned relative multiplier follow the current demand level; its test
prediction maximum is 9,051.4, above the training target maximum. There is
no fitted future trend and no current-day target in the scale. However,
squared error on ratios weights original-unit errors by the inverse squared
historical level, so this changes both loss weighting and the predictor's
form. The gain belongs to that composite model. Its roughly 1.3% test-MAE
advantage over persistence is modest, and two years in one city do not
establish general deployment reliability. The observed-weather limitation
also remains.

Implementation: `src/target_transform.py`, exposed through
`python -m src.train --target-transform` (validation only). The explicit
`--target-transform --evaluate-test` mode uses the frozen selection.
`reports/target_transformation.json` stores the selected result;
`reports/metrics.json` remains entirely untransformed.

## Exercise 5: ridge vs persistence

I recommend persistence over the untransformed ridge if over- and
underprediction each cost equally per ride and MAE is the operational loss.
Ridge improves test R² from 0.5099 to 0.5800, but raises MAE from 840.1 to
946.2: 106.1 extra rides of error per day, or 12.6%. Its validation advantage
(0.6439/836.5 versus persistence's 0.4507/900.6) does not survive on test MAE.
Ridge also requires weather inputs and model maintenance; persistence uses
one completed count. A squared-error objective could justify ridge: these
R² values imply about 14.3% lower test MSE on the same days. Without an
explicit cost that prioritizes large errors, that is insufficient to outweigh
the worse absolute error and added input requirements. Exercise 4 identifies
a separate promising tree formulation, not evidence that this ridge should
be deployed. This is a conditional recommendation for student review, not
an assumed operational cost supplied by the user.

## Attribution

NRP `qwen3` through Claude Code 2.1.328 was used for the feature/fault workflows,
the teammate reviewer, and SDK self-audits. Its response identifier was
`Qwen/Qwen3.8-Flash-Next-FP8`; the [NRP catalog](https://nrp.ai/llms/) lists
180B parameters, 6B active, and a 1M-token context. GPT-6 in Codex implemented,
orchestrated, checked, and wrote the work. No local model was downloaded,
and the NRP alias was not switched for an optional model-size comparison.

Agent-generated or modified work:

- NRP/Claude: the named-date feature test, `cnt_roll_3`, initial validation
  entry, live fault/repair runs, teammate review, and structured self-audits.
- Codex: additional contract/causality/hash tests, validation commands,
  target transformations and tests, independent audit checks and verdicts,
  `/seed-fault`, NRP setup, results, report, and staged Git history.
- The original pipeline, hook, reviewer, SDK auditor, and five original
  decision lines came from the course starter, preserved in the first commit.

Actual human instructions and decisions:

- Initially complete through Exercise 2, with NRP available if needed.
- Publish to the user-created GitHub repository, then complete the remaining
  required exercises using the supplied Jtoast65 teammate repository.

The feature, transformation, retention, and loss-based deployment choices
were agent proposals documented in `docs/DECISIONS.md`; this report does not
invent independent student judgments. The unchanged starter suite initially
accessed a test performance threshold before it was moved to validation;
that earlier exposure is disclosed, not presented as a perfectly blind
history. The student should review and own the conclusions before submission.
