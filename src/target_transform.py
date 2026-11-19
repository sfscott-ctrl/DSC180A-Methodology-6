"""Exercise 4: validate predeclared target transformations; score test explicitly.

Default: python -m src.target_transform
After committing a selection: python -m src.target_transform --evaluate-test
Canonical reports/metrics.json is never changed by this module.
"""
import argparse
import hashlib
import json

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, r2_score

from src.config import METRICS, PROCESSED, TARGET
from src.features import feature_columns
from src.train import MODELS, temporal_split

CANDIDATES = {
    "delta_lag1": ("difference", "cnt_lag_1"),
    "delta_roll7": ("difference", "cnt_roll_7"),
    "ratio_roll7": ("ratio", "cnt_roll_7"),
}
VALIDATION = METRICS.with_name("target_transform_validation.json")
SELECTION = METRICS.with_name("target_transform_selection.json")
FINAL = METRICS.with_name("target_transformation.json")


def transform_target(y, level, kind):
    y, level = np.asarray(y, dtype=float), np.asarray(level, dtype=float)
    if kind == "difference":
        return y - level
    if kind == "ratio":
        if np.any(level <= 0):
            raise ValueError("ratio transformation requires positive historical levels")
        return y / level
    raise ValueError(f"unknown transformation: {kind}")


def inverse_target(z, level, kind):
    z, level = np.asarray(z, dtype=float), np.asarray(level, dtype=float)
    if kind == "difference":
        return z + level
    if kind == "ratio":
        if np.any(level <= 0):
            raise ValueError("ratio transformation requires positive historical levels")
        return z * level
    raise ValueError(f"unknown transformation: {kind}")


def score(y, prediction):
    return {
        "r2": round(float(r2_score(y, prediction)), 4),
        "mae": round(float(mean_absolute_error(y, prediction)), 1),
    }


def fit_candidate(train, columns, name):
    kind, column = CANDIDATES[name]
    transformed = transform_target(train[TARGET], train[column], kind)
    return clone(MODELS["hgb"]).fit(train[columns], transformed)


def predict_candidate(model, part, columns, name):
    kind, column = CANDIDATES[name]
    return inverse_target(model.predict(part[columns]), part[column], kind)


def validate(frame):
    train, valid, _ = temporal_split(frame)
    columns = feature_columns(frame)
    results = {
        "n_train": len(train), "n_valid": len(valid), "features": columns,
        "selection_metric": "validation r2; validation mae breaks ties",
        "controls": {}, "candidates": {},
    }
    for name, estimator in MODELS.items():
        model = clone(estimator).fit(train[columns], train[TARGET])
        results["controls"][name] = score(valid[TARGET], model.predict(valid[columns]))
    for name in CANDIDATES:
        model = fit_candidate(train, columns, name)
        pred = predict_candidate(model, valid, columns, name)
        results["candidates"][name] = score(valid[TARGET], pred)
    return results


def evaluate_selected(frame, selection, validation):
    name = selection["selected"]
    if name not in CANDIDATES:
        raise ValueError(f"unknown selected candidate: {name}")
    train, _, test = temporal_split(frame)
    columns = feature_columns(frame)
    if columns != validation["features"]:
        raise ValueError("feature set changed after validation")
    model = fit_candidate(train, columns, name)
    prediction = predict_candidate(model, test, columns, name)
    return {
        "selected": name,
        "transformation": dict(zip(["kind", "historical_level"], CANDIDATES[name])),
        "n_train": len(train), "n_test": len(test), "features": columns,
        "valid": validation["candidates"][name],
        "test": score(test[TARGET], prediction),
        "test_prediction_range": {"min": float(prediction.min()), "max": float(prediction.max())},
        "test_controls": {name: json.loads(METRICS.read_text())[name]["test"] for name in MODELS},
        "protocol": "Selected using H1 2012, committed before this H2 2012 evaluation; no transformed test-based tuning.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluate-test", action="store_true")
    args = parser.parse_args(argv)
    frame = pd.read_parquet(PROCESSED)
    if args.evaluate_test:
        selection = json.loads(SELECTION.read_text())
        actual = hashlib.sha256(VALIDATION.read_bytes()).hexdigest()
        if selection["validation_sha256"] != actual:
            raise ValueError("validation results changed after the selection was frozen")
        result = evaluate_selected(frame, selection, json.loads(VALIDATION.read_text()))
        output = FINAL
    else:
        result, output = validate(frame), VALIDATION
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
