"""Check original-unit reconstruction and separation of validation from test."""
import numpy as np
import pandas as pd
import pytest

from src.target_transform import inverse_target, transform_target, validate
from src.features import build_features
from src.ingest import load_raw
from src.config import TARGET, VALID_END


@pytest.mark.parametrize("kind,expected", [("difference", [20., -20.]), ("ratio", [1.2, 0.8])])
def test_target_transform_and_inverse_have_known_values(kind, expected):
    transformed = transform_target([120, 80], [100, 100], kind)
    np.testing.assert_allclose(transformed, expected)
    np.testing.assert_allclose(inverse_target(transformed, [100, 100], kind), [120, 80])


def test_zero_innovation_reconstructs_persistence():
    np.testing.assert_allclose(inverse_target([0, 0], [100, 200], "difference"), [100, 200])


def test_ratio_rejects_nonpositive_history():
    with pytest.raises(ValueError, match="positive historical"):
        transform_target([120], [0], "ratio")


def test_validation_does_not_consult_test_targets():
    frame = build_features(load_raw())
    expected = validate(frame)
    altered = frame.copy()
    altered.loc[altered.dteday > VALID_END, TARGET] = np.nan
    assert validate(altered) == expected
