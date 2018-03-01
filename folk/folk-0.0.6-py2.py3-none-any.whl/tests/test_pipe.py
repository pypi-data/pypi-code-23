"""Test pipeline-related folk stuff."""

import pdpipe as pdp

from .shared import PPIPELINE


def test_pipe_base():
    for pipe in PPIPELINE:
        assert isinstance(pipe, pdp.Pipeline)
    pipe = PPIPELINE.pipeline_by_params({'lower': True})
    assert isinstance(pipe, pdp.Pipeline)
