# Part 4 self-audit (not the teammate audit in Exercise 3)

Command: `python agent/audit.py . --out reports/audit.jsonl --concurrency 1`

Model: NRP `qwen3`; SDK pin: `claude-agent-sdk==0.2.172`.
The completed audit inspected the numerical pipeline at commit `9409382`.
Its raw JSON is preserved below and in `reports/audit.jsonl`.
The first attempt exceeded the driver's 600-second limit without a final
ResultMessage; `reports/evidence/audit_attempt1.json` records that failure.
The retry bounded the reviewer to the same four screening criteria.

## Final refresh status

After completing Exercises 3–5, the same SDK command was attempted three
times against numerical code at `4d76471`. NRP returned HTTP 503, 500, and
503 before a completed result. `reports/evidence/final_audit_attempts.json`
records those failures. The JSON below and `reports/audit.jsonl` remain the
genuine earlier audit at `9409382`; they do not certify the later target
transformation. A fresh checkout independently passed all 25 tests and
regenerated all five checked result files exactly (see
`reports/evidence/completed_assignment_checks.json`). A successful final
SDK refresh remains pending endpoint recovery; rerun the documented audit
command and assess its findings before course submission.

## Codex assessment of the six findings

1. **Observed daily weather: accepted limitation.** These are retrospective
   forecast-proxy results, not demonstrated day-ahead deployment performance.
   This was already disclosed. The audit's assertions about "half" the signal
   and the size/direction of optimism are not established by the checks it
   ran; quantifying them needs an evaluation with forecast-vintage weather.
2. **Validation-only regeneration: addressed.** Added and documented
   `python -m scripts.reproduce_validation`, which regenerates both original
   validation files, retaining their historical schemas, without scoring test.
   Its files match the committed originals exactly. The audit overstates the
   numeric issue: `make all` already reproduces the same before-validation
   numbers inside `metrics_before.json`, and that is the source of the report's
   before rows. The new command closes the genuine convenience/provenance gap.
3. **Deny-by-name feature selector: valid future limitation, no current leak.**
   The actual 15 selected features pass the numerical identity check. The raw
   classification test guards new raw columns; it does not certify arbitrary
   future engineered columns. New features still require availability review
   and causal tests. No claim of universal leakage prevention is made.
4. **Warmup/lag coupling: valid future maintenance issue.** With LAG_WARMUP=7
   unchanged, both existing seven-day features retain their stated meaning.
   The added feature needs only three days. A future longer-window extension
   must decouple the existing seven-day definitions before raising that constant.
   No current score is changed by this observation.
5. **Earlier test threshold: disclosed process limitation.** The unchanged
   starter suite initially accessed a test-set threshold. It was then moved
   to validation, and the feature decision was committed before the final test
   comparison. The report does not claim literal single access or a blind
   history. The audit did not measure an amount of optimism from that exposure.
6. **Reusable estimators / future test peeking: no present numerical failure.**
   Current estimators fit from scratch with warm-start disabled; repeated full
   runs produce byte-identical metrics. A hypothetical future misuse is not
   evidence of state leakage in this run. The recorded decision chronology,
   validation-only commands, and report qualifications are the relevant controls.

An additional independent check against the raw date-to-count mapping found
zero mismatches across all 714 modeled dates for each of the four lag/rolling
features (`reports/lag_verification.json`). This uses calendar date arithmetic,
not row shifts on the already filtered modeling table.

The audit's structured verdict is leakage=none, temporal_ok=true,
baseline_reported=true, reproducible=true. It is a screening result, not a
student-authored verdict. This earlier run covered our own repository; the later teammate audit is recorded separately in `docs/AUDIT.md`.

## Auditor output, verbatim JSON line

```json
{"repo": "/Users/scarlettfeng/Documents/Codex/2026-11-18/if-your-laptop-is-not-powerful/outputs/bikeshare-open", "confidence": "high", "findings": [{"why_it_matters": "The whole point of the temporal-split and persistence-baseline discipline is a defensible forecast number. Half the surviving signal in the weather block may not exist at prediction time, so the reported ridge-vs-persistence gap (0.0701 R^2, and ridge loses on MAE) is the headline result and could shrink or reverse under a real forecast feed.", "file": "src/features.py", "line": 70, "issue": "Same-day observed weather (temp, atemp, hum, windspeed, weather_severity) is carried into the feature frame dated d and used to predict cnt on day d. These are contemporaneous covariates, not forecast-vintage inputs, so the evaluation is not a true day-ahead forecast. It is disclosed (CLAUDE.md, REPORT.md:78-83) and is not target leakage - check_identity returned clean and no feature equals or linearly restates cnt - but it means ridge's test R^2 0.5800 / MAE 946.2 are optimistic relative to a deployable model."}, {"why_it_matters": "Reproducibility check 4 is otherwise strong (fresh `make all` reproduced metrics.json and metrics_before.json byte-for-byte; env matches pins), but the specific validation numbers the feature-keeping decision is argued from cannot be regenerated from a clean checkout. A reader verifying the -0.0036 delta must instead trust an artifact of unknown provenance and schema.", "file": "src/train.py", "line": 93, "issue": "The before/after validation comparison is not reachable from any documented command. fit_and_score() accepts exclude= but the CLI exposes only --validation-only, so `python -m src.train --validation-only` can produce validation_after.json but never validation_before.json. The committed reports/validation_before.json also uses a different, flat schema ({\"ridge\": {\"r2\",\"mae\"}}, no \"valid\" nesting, no features/n_train block) that the current code cannot emit at all. REPORT.md's \"Before\" rows (0.6475/832.9, 0.2185/1296.6) come from that file, while only metrics_before.json (full-pipeline, includes test) is reproducible."}, {"why_it_matters": "This is the exact failure mode the repo's own leakage_demo.py exists to teach (R^2 = 1.0 from a restatement of the target). The gate has no default-deny for derived columns, so the protection decays the moment someone adds a feature without editing config.py.", "file": "src/features.py", "line": 86, "issue": "feature_columns() is deny-by-name: it takes every numeric-dtype column in the built frame minus the FORBIDDEN set, so safety is a property of a column's name rather than of how it was constructed. It is correct today - the parquet still carries casual, registered, cnt_2d_bfr, days_since_2011 and instant, and I confirmed all are absent from the 15 selected columns - but any future target-derived column added in build_features() (an unshifted rolling mean, a cnt residual feature) enters the model by default. test_no_forbidden_features (tests/test_leakage.py:25) guards only the known names, and test_every_raw_column_is_classified (tests/test_contract.py:28) inspects raw CSV columns, not derived ones."}, {"why_it_matters": "Reported metrics and the named-date test in tests/test_leakage.py are keyed to feature names, not definitions. A config bump changes what cnt_lag_7 means without changing any code path that would flag it, so a future before/after comparison could attribute a change to the wrong feature.", "file": "src/features.py", "line": 76, "issue": "cnt_lag_7 is built as out[TARGET].shift(LAG_WARMUP), fusing the lag length and the warmup/drop-window constant into one variable. config.py:58-61 and the comment at features.py:74 instruct 'if you add a longer lag, raise LAG_WARMUP' - doing so silently redefines cnt_lag_7 into, say, cnt_lag_14 while keeping its column name and its metric slot."}, {"why_it_matters": "Test-set contamination is a past decision, not a property of the present code. I can verify the pipeline today does not tune on H2 2012, but I cannot verify the retained cnt_roll_3 and hyperparameter choices were never informed by the earlier threshold-bearing suite, so the reported test numbers carry a small, self-declared optimism.", "file": "REPORT.md", "line": 51, "issue": "The report discloses that the starter's contract test asserted a test-set performance threshold and was only later moved to validation: 'this report does not claim the held-out data were literally accessed only once.' The current tree is clean - I confirmed no test-set threshold exists (tests/test_contract.py:68 scores the valid split) and the selection artifact records selection_data = 2012-01-01..2012-06-30, test_scores_reviewed_for_decision = False - but the earlier exposure is unbounded and unverifiable from the code."}, {"why_it_matters": "The current numbers are unaffected (fit() fully overwrites Ridge/pipeline state and PersistenceBaseline fits nothing; I re-ran make all and got identical output), but the structure raises no error if a future experiment reuses a fitted estimator or makes a second selection pass after seeing test.", "file": "src/train.py", "line": 79, "issue": "Models are mutable module-level singletons in MODELS, refit in dict order on every fit_and_score() call, so state can carry across calls in a long-lived process or a future loop over feature sets; tests/test_contract.py:66 refits the shared MODELS['ridge'] object as a side effect. There is also no artifact hash or single-use guard preventing a later run from re-reading the printed test scores and iterating again - 'never tune on test' is enforced by convention only."}], "reproducible": true, "leakage": "none", "baseline_reported": true, "temporal_ok": true}
```
