# Seeded faults — Exercises 1 and 2

## Exercise 1: test written before feature

Claude Code invoked `/new-feature cnt_roll_3` against NRP `qwen3`.
The first turn stopped after adding the test and observing the missing-column failure.
The next commit implements the feature. The captured run used the shared
working tree, where the driver had also added the raw-column contract test
(committed with the implementation). Therefore it shows 15 passing tests;
checking out the isolated failing-feature-test commit gives the same missing
column failure with 14 other tests passing. The transcript records this
concurrent work explicitly. Actual captured tail of `make ... test 2>&1 | tail -30` (the full tool invocation is in `reports/evidence/01-feature-test.json`):

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

## Fault 4: Bash cp into raw data bypasses the Edit/Write hook

This experiment ran in a disposable copy at `work/fault4/repo`, containing
the completed feature and pre-hash-guard tests. The deliverable CSV was
never overwritten. A separate CSV changed only the 2011-07-01 temperature
value by +10 (CSV serialization also changed); Bash executed:

```bash
cp "$experiment/corrupt.csv" data/raw/bike_daily.csv
make test
cp "$experiment/original.csv" data/raw/bike_daily.csv
```

The actual script included a trap to restore the original on exit and
printed SHA256 before, after, and after restoration. The harness ran one
Bash tool call; **zero PostToolUse hook events** were recorded, because its
matcher is `Edit|Write`. Its source deny rules therefore did not intercept
this Bash cp. Actual output:

```text
Original raw SHA256: a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc  data/raw/bike_daily.csv
After Bash cp SHA256: 53edf223d554e7edce46ac78b768ca600fb8cec0b5de9866d37e9d9ef4ab4236  data/raw/bike_daily.csv
Temperature after cp: 35.957499999999996
python -m pytest tests/ -q
..................                                                       [100%]
18 passed in 2.11s
Restored raw SHA256: a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc  data/raw/bike_daily.csv

```

The 18 pre-guard tests pass despite the changed bytes. The temperature
printed is the value on one named date, not a dataset mean (the model's
summary called it a mean incorrectly). Restoration returns to the original
hash. No repair turn was needed: restoration was planned in the script.
The successful harness invocation used two turns (Bash, then summary).
An earlier invocation was denied by the launcher's exact-command allow rule
because the model appended a dot argument; it did not execute. That attempt
is retained separately as `06-raw-bash.json`, and the successful run is
`06b-raw-bash.json`. Project Edit/Write deny rules remained unchanged.

### What catches it now

The implemented SHA256 guard in `make data` and `test_raw_file_matches_pinned_hash`
detects altered raw bytes, including changes that preserve the schema.
A Stop hook invoking the full suite would also detect this with the guard in
place. A Stop hook invoking the old suite would not: the old suite stayed
green. A Bash PreToolUse rule inspecting writes or filesystem-level write
protection could prevent the write rather than detect it afterwards.

The same corrupt copy was tested in another disposable checkout containing
the guard; both `make data` and `make test` failed. Actual output:

```text
Controlled copy with the new raw SHA256 guard.
Command: cp corrupt.csv data/raw/bike_daily.csv

$ make data
python -m src.ingest
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/scarlettfeng/Documents/Codex/2026-11-18/if-your-laptop-is-not-powerful/work/fault4-guarded/repo/src/ingest.py", line 43, in <module>
    verify_raw_hash()
    ~~~~~~~~~~~~~~~^^
  File "/Users/scarlettfeng/Documents/Codex/2026-11-18/if-your-laptop-is-not-powerful/work/fault4-guarded/repo/src/ingest.py", line 28, in verify_raw_hash
    raise ValueError(f"raw data SHA256 mismatch: expected {RAW_SHA256}; got {actual}")
ValueError: raw data SHA256 mismatch: expected a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc; got 53edf223d554e7edce46ac78b768ca600fb8cec0b5de9866d37e9d9ef4ab4236
make: *** [data] Error 1

exit_code=2

$ make test
python -m pytest tests/ -q
..F.................                                                     [100%]
=================================== FAILURES ===================================
______________________ test_raw_file_matches_pinned_hash _______________________

    def test_raw_file_matches_pinned_hash():
>       verify_raw_hash()

tests/test_contract.py:34: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

path = PosixPath('/Users/scarlettfeng/Documents/Codex/2026-11-18/if-your-laptop-is-not-powerful/work/fault4-guarded/repo/data/raw/bike_daily.csv')

    def verify_raw_hash(path: Path = RAW) -> None:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != RAW_SHA256:
>           raise ValueError(f"raw data SHA256 mismatch: expected {RAW_SHA256}; got {actual}")
E           ValueError: raw data SHA256 mismatch: expected a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc; got 53edf223d554e7edce46ac78b768ca600fb8cec0b5de9866d37e9d9ef4ab4236

src/ingest.py:28: ValueError
=========================== short test summary info ============================
FAILED tests/test_contract.py::test_raw_file_matches_pinned_hash - ValueError...
1 failed, 19 passed in 2.06s
make: *** [test] Error 1

exit_code=2

```

Actual guard implementation diff:

```diff
diff --git a/src/config.py b/src/config.py
index 532f40b..2e36aff 100644
--- a/src/config.py
+++ b/src/config.py
@@ -3,6 +3,7 @@ from pathlib import Path
 
 ROOT = Path(__file__).resolve().parents[1]
 RAW = ROOT / "data" / "raw" / "bike_daily.csv"
+RAW_SHA256 = "a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc"
 PROCESSED = ROOT / "data" / "processed" / "features.parquet"
 METRICS = ROOT / "reports" / "metrics.json"
 
diff --git a/src/ingest.py b/src/ingest.py
index 6654075..70135c5 100644
--- a/src/ingest.py
+++ b/src/ingest.py
@@ -2,12 +2,14 @@
 
 Run: python -m src.ingest
 """
+import hashlib
 import sys
 import urllib.request
+from pathlib import Path
 
 import pandas as pd
 
-from src.config import DATA_URL, RAW
+from src.config import DATA_URL, RAW, RAW_SHA256
 
 EXPECTED_MIN_ROWS = 700
 REQUIRED_COLS = {"dteday", "cnt", "casual", "registered", "temp", "hum", "windspeed"}
@@ -20,6 +22,12 @@ def download(force: bool = False) -> None:
     urllib.request.urlretrieve(DATA_URL, RAW)
 
 
+def verify_raw_hash(path: Path = RAW) -> None:
+    actual = hashlib.sha256(path.read_bytes()).hexdigest()
+    if actual != RAW_SHA256:
+        raise ValueError(f"raw data SHA256 mismatch: expected {RAW_SHA256}; got {actual}")
+
+
 def load_raw() -> pd.DataFrame:
     df = pd.read_csv(RAW, parse_dates=["dteday"])
     missing = REQUIRED_COLS - set(df.columns)
@@ -32,5 +40,6 @@ def load_raw() -> pd.DataFrame:
 
 if __name__ == "__main__":
     download(force="--force" in sys.argv)
+    verify_raw_hash()
     df = load_raw()
     print(f"OK ingest: {len(df)} rows, {df.dteday.min().date()} -> {df.dteday.max().date()}")
diff --git a/tests/test_contract.py b/tests/test_contract.py
index a28398b..37e74df 100644
--- a/tests/test_contract.py
+++ b/tests/test_contract.py
@@ -3,9 +3,9 @@ import pandas as pd
 import pytest
 from sklearn.metrics import r2_score
 
-from src.config import CLASSIFIED_RAW_COLS, LAG_WARMUP, TARGET
+from src.config import CLASSIFIED_RAW_COLS, LAG_WARMUP, RAW, TARGET
 from src.features import build_features, feature_columns, reindex_to_calendar
-from src.ingest import load_raw
+from src.ingest import load_raw, verify_raw_hash
 from src.train import MODELS, temporal_split
 
 
@@ -30,6 +30,17 @@ def test_every_raw_column_is_classified(raw):
     assert not unknown, f"unclassified raw columns: {sorted(unknown)}"
 
 
+def test_raw_file_matches_pinned_hash():
+    verify_raw_hash()
+
+
+def test_hash_guard_rejects_mutation(tmp_path):
+    modified = tmp_path / "bike_daily.csv"
+    modified.write_bytes(RAW.read_bytes() + b"\n")
+    with pytest.raises(ValueError, match="raw data SHA256 mismatch"):
+        verify_raw_hash(modified)
+
+
 def test_only_expected_rows_are_dropped(raw, feats):
     """Rows may only vanish for the lag warm-up or downstream of a genuinely
     absent day -- never because an encoder produced a silent NaN.
```
