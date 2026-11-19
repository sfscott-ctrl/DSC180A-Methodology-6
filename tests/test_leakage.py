"""The tests that make the agent honest.

test_no_forbidden_features is the single most valuable test in this repo:
casual + registered == cnt exactly, so any model handed those columns
scores R^2 = 1.0 and looks brilliant while having learned nothing.
"""
import pandas as pd
import pytest

from src.config import FORBIDDEN, TARGET
from src.features import build_features, feature_columns
from src.ingest import load_raw


@pytest.fixture(scope="module")
def feats():
    return build_features(load_raw())


def test_leakage_identity_holds(feats):
    """Documents *why* casual and registered are forbidden."""
    assert (feats.casual + feats.registered == feats[TARGET]).all()


def test_no_forbidden_features(feats):
    """Guards the gate, not the data: feature_columns() excludes FORBIDDEN by
    construction, so this cannot discover a *new* leaky column. What it
    catches is someone editing feature_columns() or FORBIDDEN -- which is
    exactly the fault the Step 7 hook demonstrates."""
    cols = set(feature_columns(feats))
    assert not (cols & FORBIDDEN), f"forbidden columns in feature set: {cols & FORBIDDEN}"


def test_lags_are_true_calendar_lags(feats):
    """cnt_lag_1 for date d must equal cnt on d-1, in calendar days."""
    by_date = feats.set_index("dteday")[TARGET]
    checked = 0
    for date, lag in feats.set_index("dteday").cnt_lag_1.items():
        prev = date - pd.Timedelta(days=1)
        if prev in by_date.index:
            assert lag == pytest.approx(by_date[prev]), f"bad lag at {date.date()}"
            checked += 1
    assert checked > 600, "too few rows actually verified"


def test_lag_is_not_the_target(feats):
    assert not (feats.cnt_lag_1 == feats[TARGET]).all()


def test_rolling_mean_excludes_today(feats):
    """cnt_roll_7 must be the mean of the 7 calendar days *before* today."""
    by_date = feats.set_index("dteday")[TARGET]
    date = feats.dteday.iloc[200]
    window = [date - pd.Timedelta(days=k) for k in range(1, 8)]
    if all(d in by_date.index for d in window):
        expected = sum(by_date[d] for d in window) / 7
        assert feats.set_index("dteday").cnt_roll_7[date] == pytest.approx(expected)


def test_roll_3_excludes_today(feats):
    """cnt_roll_3 is the mean of cnt on d-1, d-2, d-3 -- hand-computed.

    Dates and counts are literals read off data/raw/bike_daily.csv, not
    derived from the frame under test, so this fails if the feature is
    missing, misaligned, or built without shift(1):
      2011-02-16 -> 2115, 2011-02-15 -> 1815, 2011-02-14 -> 1913
      expected   -> (2115 + 1815 + 1913) / 3 = 1947.666...
    A same-day window (02-17 = 2475 in place of 02-14) would give 2135.0,
    and 2011-02-17 itself is 2475 -- both distinguishable from 1947.67.
    2011-02-14 is 43 days into the series, well past LAG_WARMUP, and no
    calendar day is missing in this window (the only gap is 2011-03-10).
    """
    by_date = feats.set_index("dteday")
    date = pd.Timestamp("2011-02-17")
    for day, cnt in [("2011-02-14", 1913), ("2011-02-15", 1815), ("2011-02-16", 2115)]:
        assert by_date.loc[pd.Timestamp(day), TARGET] == cnt, f"raw data moved: {day}"
    expected = (2115 + 1815 + 1913) / 3
    assert by_date["cnt_roll_3"][date] == pytest.approx(expected)


def test_no_missing_values(feats):
    assert feats[feature_columns(feats)].isna().sum().sum() == 0


def test_dates_are_sorted_and_unique(feats):
    assert feats.dteday.is_monotonic_increasing
    assert feats.dteday.is_unique
