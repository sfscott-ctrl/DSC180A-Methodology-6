# Seeded faults — Exercises 1 and 2

## Exercise 1: test written before feature

Claude Code invoked `/new-feature cnt_roll_3` against NRP `qwen3`.
The first turn stopped after adding the test and observing the missing-column failure.
The next commit implements the feature. Actual captured tail of `make ... test 2>&1 | tail -30` (the full tool invocation is in `reports/evidence/01-feature-test.json`):

```text
        --------
        >>> unique_index = pd.Index(list("abc"))
        >>> unique_index.get_loc("b")
        1
    
        >>> monotonic_index = pd.Index(list("abbc"))
        >>> monotonic_index.get_loc("b")
        slice(1, 3, None)
    
        >>> non_monotonic_index = pd.Index(list("abcb"))
        >>> non_monotonic_index.get_loc("b")
        array([False,  True, False,  True])
        """
        casted_key = self._maybe_cast_indexer(key)
        try:
            return self._engine.get_loc(casted_key)
        except KeyError as err:
            if isinstance(casted_key, slice) or (
                isinstance(casted_key, abc.Iterable)
                and any(isinstance(x, slice) for x in casted_key)
            ):
                raise InvalidIndexError(key) from err
>           raise KeyError(key) from err
E           KeyError: 'cnt_roll_3'

../../work/venv/lib/python3.13/site-packages/pandas/core/indexes/base.py:3648: KeyError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_roll_3_excludes_today - KeyError: 'cnt_rol...
1 failed, 15 passed in 2.56s
make: *** [test] Error 1

```

## Fault 1: forbidden casual predictor

Executed with Claude Code/NRP qwen3 via `/seed-fault` in one invocation
(10 harness turns including setup). After the first failing
automatic hook, repair took **3 assistant response(s)**, counting unique
API message IDs through the restoring Edit. There was **one source repair
attempt**, restoring the original expression; no tests were weakened.
The count includes the requested red `make test` call, not just the repair.

Exact injected diff (the repair reverses it):

```diff
--- src/features.py (healthy)
+++ src/features.py (seeded)
@@ -1 +1 @@
-    return [c for c in numeric if c not in FORBIDDEN]
+    return [c for c in numeric if c not in FORBIDDEN] + ["casual"]
```

Actual red `make test` output:

```text
python -m pytest tests/ -q
......F...........                                                       [100%]
=================================== FAILURES ===================================
__________________________ test_no_forbidden_features __________________________

feats =         dteday  instant  season  ...  cnt_lag_7   cnt_roll_7   cnt_roll_3
0   2011-01-10     10.0  WINTER  ...     134....142857  2183.333333
713 2012-12-31    731.0  WINTER  ...      920.0  1531.428571  2077.333333

[714 rows x 29 columns]

    def test_no_forbidden_features(feats):
        """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
        construction, so this cannot discover a *new* leaky column. What it
        catches is someone editing feature_columns() or FORBIDDEN -- which is
        exactly the fault the Step 7 hook demonstrates."""
        cols = set(feature_columns(feats))
>       assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"
E       AssertionError: forbidden columns in feature set: {'casual'}
E       assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_3', 'cnt_roll_7', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'days_since_2011', 'instant', 'registered', ...})

tests/test_leakage.py:31: AssertionError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed, 17 passed in 1.72s
make: *** [test] Error 1
```

Automatic `PostToolUse:Edit` hook: exit **2**, stderr verbatim:

```text
Leakage tests failed after editing /Users/scarlettfeng/Documents/Codex/2026-11-18/if-your-laptop-is-not-powerful/outputs/bikeshare-open/src/features.py:
feats =         dteday  instant  season  ...  cnt_lag_7   cnt_roll_7   cnt_roll_3
0   2011-01-10     10.0  WINTER  ...     134....142857  2183.333333
713 2012-12-31    731.0  WINTER  ...      920.0  1531.428571  2077.333333

[714 rows x 29 columns]

    def test_no_forbidden_features(feats):
        """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
        construction, so this cannot discover a *new* leaky column. What it
        catches is someone editing feature_columns() or FORBIDDEN -- which is
        exactly the fault the Step 7 hook demonstrates."""
        cols = set(feature_columns(feats))
>       assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"
E       AssertionError: forbidden columns in feature set: {'casual'}
E       assert not ({'atemp', 'casual', 'cnt_lag_1', 'cnt_lag_7', 'cnt_roll_3', 'cnt_roll_7', ...} & {'casual', 'cnt', 'cnt_2d_bfr', 'days_since_2011', 'instant', 'registered', ...})

tests/test_leakage.py:31: AssertionError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_no_forbidden_features - AssertionError: fo...
1 failed, 9 passed in 0.35s
```

Restoring Edit hook: exit **0**, stderr ``. Final test run:

```text
python -m pytest tests/ -q
..................                                                       [100%]
18 passed in 1.39s
```

Machine-readable tool calls and hook events: `reports/evidence/03-fault-forbidden.json`.

## Fault 2: rolling mean includes the current target

Executed with Claude Code/NRP qwen3 via `/seed-fault` in one invocation
(10 harness turns including setup). After the first failing
automatic hook, repair took **2 assistant response(s)**, counting unique
API message IDs through the restoring Edit. There was **one source repair
attempt**, restoring the original expression; no tests were weakened.
The count includes the requested red `make test` call, not just the repair.

Exact injected diff (the repair reverses it):

```diff
--- src/features.py (healthy)
+++ src/features.py (seeded)
@@ -1 +1 @@
-    out["cnt_roll_7"] = out[TARGET].shift(1).rolling(LAG_WARMUP).mean()
+    out["cnt_roll_7"] = out[TARGET].rolling(LAG_WARMUP).mean()
```

Actual red `make test` output:

```text
python -m pytest tests/ -q
...........F........                                                     [100%]
=================================== FAILURES ===================================
_______________________ test_rolling_mean_excludes_today _______________________

feats =         dteday  instant  season  ...  cnt_lag_7   cnt_roll_7   cnt_roll_3
0   2011-01-10     10.0  WINTER  ...     134....428571  2183.333333
713 2012-12-31    731.0  WINTER  ...      920.0  1789.857143  2077.333333

[714 rows x 29 columns]

    def test_rolling_mean_excludes_today(feats):
        """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
        by_date = feats.set_index("dteday")[TARGET]
        date = feats.dteday.iloc[200]
        window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
        if all(d in by_date.index for d in window):
            expected = sum(by_date[d] for d in window) / 7
>           assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)
E           assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
E             
E             comparison failed
E             Obtained: 4389.0
E             Expected: 4414.857142857143 ± 0.00441486

tests/test_leakage.py:57: AssertionError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 19 passed in 1.73s
make: *** [test] Error 1
```

Automatic `PostToolUse:Edit` hook: exit **2**, stderr verbatim:

```text
Leakage tests failed after editing /Users/scarlettfeng/Documents/Codex/2026-11-18/if-your-laptop-is-not-powerful/outputs/bikeshare-open/src/features.py:
[714 rows x 29 columns]

    def test_rolling_mean_excludes_today(feats):
        """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
        by_date = feats.set_index("dteday")[TARGET]
        date = feats.dteday.iloc[200]
        window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
        if all(d in by_date.index for d in window):
            expected = sum(by_date[d] for d in window) / 7
>           assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)
E           assert np.float64(4389.0) == 4414.857142857143 ± 0.00441486
E             
E             comparison failed
E             Obtained: 4389.0
E             Expected: 4414.857142857143 ± 0.00441486

tests/test_leakage.py:57: AssertionError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 9 passed in 0.36s
```

Restoring Edit hook: exit **0**, stderr ``. Final test run:

```text
python -m pytest tests/ -q
....................                                                     [100%]
20 passed in 2.00s
```

Machine-readable tool calls and hook events: `reports/evidence/04-fault-rolling.json`.

## Fault 3: unknown-weather error removed

Executed with Claude Code/NRP qwen3 via `/seed-fault` in one invocation
(11 harness turns including setup). After the first failing
automatic hook, repair took **2 assistant response(s)**, counting unique
API message IDs through the restoring Edit. There was **one source repair
attempt**, restoring the original expression; no tests were weakened.
The count includes the requested red `make test` call, not just the repair.

Exact injected diff (the repair reverses it):

```diff
--- src/features.py (healthy)
+++ src/features.py (seeded)
@@ -1 +1 @@
-        raise ValueError(f"unmapped weather labels: {sorted(unknown)}")
+        pass
```

Actual red `make test` output:

```text
python -m pytest tests/ -q
...............F....                                                     [100%]
=================================== FAILURES ===================================
_________________ test_weather_encoder_rejects_unknown_labels __________________

    def test_weather_encoder_rejects_unknown_labels():
>       with pytest.raises(ValueError, match="unmapped weather labels.*UNKNOWN"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_leakage.py:91: Failed
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_weather_encoder_rejects_unknown_labels - F...
1 failed, 19 passed in 1.51s
make: *** [test] Error 1
```

Automatic `PostToolUse:Edit` hook: exit **2**, stderr verbatim:

```text
Leakage tests failed after editing /Users/scarlettfeng/Documents/Codex/2026-11-18/if-your-laptop-is-not-powerful/outputs/bikeshare-open/src/features.py:
........F.                                                               [100%]
=================================== FAILURES ===================================
_________________ test_weather_encoder_rejects_unknown_labels __________________

    def test_weather_encoder_rejects_unknown_labels():
>       with pytest.raises(ValueError, match="unmapped weather labels.*UNKNOWN"):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_leakage.py:91: Failed
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_weather_encoder_rejects_unknown_labels - F...
1 failed, 9 passed in 0.33s
```

Restoring Edit hook: exit **0**, stderr ``. Final test run:

```text
python -m pytest tests/ -q
....................                                                     [100%]
20 passed in 1.24s
```

Machine-readable tool calls and hook events: `reports/evidence/05-fault-weather.json`.
