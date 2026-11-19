"""Reproduce the original validation-only comparison without scoring test.

Run from the repository root: python -m scripts.reproduce_validation
The original flat before schema is retained for historical consistency.
"""
import json

from src.config import METRICS
from src.train import MODELS, fit_and_score


def main():
    before_full = fit_and_score(validation_only=True, exclude=("cnt_roll_3",))
    before = {name: before_full[name]["valid"] for name in MODELS}
    after = fit_and_score(validation_only=True)
    METRICS.parent.mkdir(parents=True, exist_ok=True)
    METRICS.with_name("validation_before.json").write_text(json.dumps(before, indent=2) + "\n")
    METRICS.with_name("validation_after.json").write_text(json.dumps(after, indent=2) + "\n")
    for name in MODELS:
        old = before[name]["r2"]
        new = after[name]["valid"]["r2"]
        print(f"{name}: validation R2 {old:.4f} -> {new:.4f}; delta {new-old:+.4f}")


if __name__ == "__main__":
    main()
