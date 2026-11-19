# Exercise 3: teammate audit

- Repository: [Jtoast65/methodology-6](https://github.com/Jtoast65/methodology-6)
- Audited snapshot: [`f7bf8c5ba7ee89fff9e0758335fda41f7968e4e6`](https://github.com/Jtoast65/methodology-6/tree/f7bf8c5ba7ee89fff9e0758335fda41f7968e4e6)
- Date: 2026-11-18, America/Los_Angeles.
- Reviewer: NRP `qwen3` through Claude Code 2.1.328, using the trusted
  `.claude/agents/leakage-auditor.md` five-check role. The native CLI
  `--agent leakage-auditor` selection is the headless equivalent of the
  assignment's `/leakage-auditor` request; the prompt also starts with that name.
- This was a separate context with only the teammate checkout under review.
  Its settings/hooks were not loaded. Source was inspected before execution.
  The review made no source changes and sent no message to the teammate.
- Actual run: 19 harness turns, successful ResultMessage. Its exact invocation
  and diagnostic tool trace are in `reports/evidence/peer_audit_invocation.json`
  and `reports/evidence/peer_audit_trace.json`. The reviewer ran `make all`
  and `make test`; 18 tests passed and both result files match the commit.

## Independent verdict

None of the findings establishes an incorrect number in the current committed results. I partly agree with finding 1: the transformation subsection should explicitly compare both baselines, especially because its test MAE is 891.2 versus persistence's 840.1 (51.1 rides, or about 6.1%, worse), despite an R² advantage of 0.0520. That changes the practical interpretation, not the computed scores; a weak untransformed tree under distribution shift is not itself leakage. Finding 2 does not prove test-based tuning: the report discloses later reruns after a frozen choice, and recomputing a fixed model is distinct from choosing it on test. I reject finding 3 as a current pipeline defect: removing a day in memory legitimately creates additional missing-history rows, whereas the actual ingest hash rejects that changed CSV; the proposed assertions would not remedy its scenario. Finding 4 correctly notices the teammate-audit deliverable is still marked pending, but that is not a numerical methodology failure, and a different local workspace path does not prove the self-audit used a different repository. The claim that all checks are guaranteed by the feature-name gate is false; the temporal, raw-hash, row-loss, and arithmetic tests are independent. The minor NaN-identity claim is also contradicted by a direct check: dropping one missing alias leaves 727 exact matching rows, with residual 1.42e-14, which still triggers leakage detection. The reproduction and independent calendar checks support the current retrospective results; observed-weather availability remains the already-disclosed limit on operational forecasting. These are Codex's judgments for student review, separate from the model's verbatim output.

Supporting independent measurements are in
`reports/evidence/peer_independent_checks.json`: the actual raw hash, artifact
comparisons, all 714 calendar-aligned values of each existing lag/mean,
the boundary-gap/hash-guard experiment, and the missing-alias identity check.
The original teammate source and raw CSV remain unchanged.

## /leakage-auditor output, verbatim

The following includes claims rejected above; preservation is not endorsement.

```text


**Verification performed:** read `src/config.py`, `features.py`, `train.py`, `ingest.py`, all tests, `agent/audit.py`, `REPORT.md`, `docs/*`; ran `make all` and `make test` once in the pinned venv (`/work/venv`, Python 3.13.1, numpy 2.5.3 / pandas 3.0.5 / sklearn 1.9.1 = `requirements.txt`). 18 tests pass; both committed JSON files regenerate byte-identical (`git status` clean). Every REPORT table value, 714/348/182/184 rows, and the 56.52%-above-train-max claim reproduce.

**Checks 1, 2, 3 pass.** No selected feature restates `cnt` (14 columns, `lstsq` residual ≥ 1e-6 holds); `cnt_lag_1/lag_7/roll_7/temp_demand_lag_1` (features.py:74-78) all shift before aggregating; `temp_demand_lag_1` = yesterday's temp × yesterday's cnt, confirmed at 2011-06-15. `StandardScaler`/`DummyRegressor` fit inside `train[cols]` only, and because the train window ends at `TRAIN_END` no lagged feature can reach past the boundary. `reindex_to_calendar` (features.py:44-50) covers the interior gap; `casual/registered/cnt/instant/yr/days_since_2011/cnt_2d_bfr` never enter `feature_columns`.

**Findings (4):**

1. **Unreported baseline — the transformation study's headline has no baseline row.** `src/train.py:104-119` / `reports/target-transformation.json` / `REPORT.md:30` report only R² 0.6329 / MAE 784.7 (valid) and 0.5619 / 891.2 (test). Check 5 fails for these numbers. The scenario that embarrasses it: `predictions = part["cnt_lag_1"] + model.predict(...)` (train.py:114) *is* persistence plus a learned delta, yet the table's comparison anchor is the **feature-comparison `hgb` row** (0.2370/1284.5), which itself contains a leakage-shaped hole — it trains on 2011 only and cannot extrapolate (56.5% of test days exceed `train.cnt.max()` = 6043), while persistence (0.5099/840.1) beats that. Framed as "approaches ridge," the +0.40 gain over the broken `hgb` row is not evidence the delta term is useful. Fix: emit both baselines inside `target_change_scores` (score `MODELS["baseline_persistence"]` on `part[cols]` and the train-mean dummy) and compare the transformation against persistence, not against `hgb`.

2. **"Test set touched once" is contradicted by the diff (`docs/DECISIONS.md:7`; `REPORT.md:32` "fixed from validation before final test scoring").** Test R²/MAE are printed by `score_models` (train.py:72) for both the `after` arm (train.py:99) and `target_change_scores`, and `make all` → `make train` runs both. `DECISIONS.md:12` records that the agent ran `make train` *after* the transformation choice was recorded, and commit `f7bf8c5` follows `e9fe997`. So the fixed final test scores were visible more than once, and the claim that no decision changed afterwards cannot be established from the repo. Fix: gate test-split scoring behind an explicit `--final` flag, or log the single touch date in DECISIONS.

3. **Row-loss assertion bounds the total but not the location (`tests/test_contract.py:45-49`).** I simulated an absent calendar day (the config's own failure mode): a gap at **2011-12-31** gives `lost = 21 == allowed_loss`, passes, and silently drops the last training day (`n_train` 348→347); a mid-2011 gap also passes while dropping 7 more training rows (`n_train` 340). Since the train split is 348 rows here, a mirror with a boundary gap changes every number with no failing test. Fix: add `assert set(feats.dteday) <= set(raw.dteday)` and assert the retained dates span `raw`'s range within `LAG_WARMUP` of each end.

4. **Peer audit is absent, not pending paperwork (`docs/AUDIT.md:1-16`, `REPORT.md:52`).** The only audit artifact, `reports/audit.jsonl`, names `https-dsc-capstone-org-2026-27/outputs/bikeshare-open` — not this repo — and is a summary row with `findings: []`; no session evidence for the claimed `check_identity` call exists. Self-auditing one's own pipeline cannot fail checks 1-5, all of which are enforced by the same `feature_columns` gate the audit was supposed to test independently.

Minor, non-numeric: `agent/audit.py:63` drops NaN rows before testing linear identities and so could clear a copy of `cnt` that is NaN on the dropped day; `features.py:80`'s blanket `dropna()` would also delete `temp`/`hum` NaNs unaccounted for by `test_only_expected_rows_are_dropped`.
```
