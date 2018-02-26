"""Test model-related folk stuff."""

from .shared import (
    LogisticRegression,
    PMODEL,
)


def test_model_base():
    for model in PMODEL:
        assert isinstance(model, LogisticRegression)
    model = PMODEL.model_by_params({'penalty': 'l1', 'C': 0.3})
    assert isinstance(model, LogisticRegression)
