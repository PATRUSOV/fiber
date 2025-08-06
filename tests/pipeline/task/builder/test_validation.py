import pytest
from typing import Generic, List, Sequence, Tuple, Type, TypeVar

from fiber.step import Step
from fiber.pipeline.task.builder.validation import (
    StepSequenceValidator,
    EmptySequenceError,
    IncompatibleStepTypesError,
    InvalidPipelineEndpointsError,
)


class StartStep(Step[None, int]): ...


class RIncStep(Step[int, str]): ...


class LIncStep(Step[str, int]): ...


class FinalStep(Step[int, None]): ...


@pytest.fixture
def valid_steps() -> Sequence[Type[Step]]:
    return StartStep, FinalStep


def test_build_from_valid_step_sequence(valid_steps: Tuple[Type[Step], ...]):
    StepSequenceValidator.validate(valid_steps)


def test_with_empty_sequence():
    with pytest.raises(EmptySequenceError):
        StepSequenceValidator.validate([])


def test_incorrect_start_type():
    with pytest.raises(InvalidPipelineEndpointsError):
        StepSequenceValidator.validate([LIncStep, FinalStep])


def test_incorrect_final_type():
    with pytest.raises(InvalidPipelineEndpointsError):
        StepSequenceValidator.validate([StartStep, RIncStep])


@pytest.mark.parametrize(
    "steps",
    [
        (StartStep, RIncStep, FinalStep),
        (StartStep, LIncStep, FinalStep),
    ],
)
def test_build_from_incorrect_step_sequence(steps: Tuple[Type[Step], ...]):
    with pytest.raises(IncompatibleStepTypesError):
        StepSequenceValidator.validate(steps)


def test_single_step_validation():
    class SingleStep(Step[None, None]): ...

    StepSequenceValidator.validate([SingleStep])


def test_build_from_steps_with_typed_generics():
    T = TypeVar("T")

    class Box(Generic[T]): ...

    class StartStep(Step[None, List[Box[int]]]): ...

    class FinalStep(Step[List[Box[int]], None]): ...

    StepSequenceValidator.validate([StartStep, FinalStep])


def test_build_from_steps_with_invalid_typed_generics():
    T = TypeVar("T")

    class Box(Generic[T]): ...

    class StartStep(Step[None, List[Box[int]]]): ...

    class FinalStep(Step[List[Box[str]], None]): ...

    with pytest.raises(IncompatibleStepTypesError):
        StepSequenceValidator.validate([StartStep, FinalStep])
