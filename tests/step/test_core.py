import pytest

from src.step import Step, StepTypeParametersMissing


def test_step_without_generic():
    with pytest.raises(StepTypeParametersMissing):

        class NoGenericStep(Step): ...
