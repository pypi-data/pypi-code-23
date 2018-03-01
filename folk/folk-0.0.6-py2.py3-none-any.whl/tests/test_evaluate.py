"""Test folk's evaluate module."""

import pytest


from folk import (
    eval_param_pipeline_n_model,
)

from .shared import (
    MODEL_PGRID,
    PIPE_PGRID,
    PPIPELINE,
    PMODEL,
    TEST_METRICS_DB,
    _test_df,
    _metrics_collection,
    _clean_db,
)


@pytest.fixture(scope="session", autouse=True)
def prep_and_teardown(request):
    # Will be executed before the first test
    _clean_db()

    yield

    # Will be executed after the last test
    _clean_db()


def test_base_eval():
    eval_param_pipeline_n_model(
        param_pipeline=PPIPELINE,
        param_model=PMODEL,
        dataset=_test_df(),
        metric_db=TEST_METRICS_DB,
        n_folds=2,
    )


if __name__ == "__main__":
    test_base_eval()
    model_permutations = len(MODEL_PGRID)
    pipeline_permutations = len(PIPE_PGRID)
    total_experiments = pipeline_permutations * model_permutations
    metric_collection = _metrics_collection()
    assert metric_collection.count({}) == total_experiments
