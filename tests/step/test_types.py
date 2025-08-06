import pytest

from fiber.step import Step, get_step_types, NotAStepError


def test_getting_valid_step_types():
    class ValidStep(Step[int, str]): ...

    in_t, out_t = get_step_types(ValidStep)
    assert in_t is int and out_t is str


def test_getting_not_a_step_types():
    class NotAStep: ...

    with pytest.raises(NotAStepError):
        get_step_types(NotAStep)  # type: ignore (тест на шаг который не наследует Step)
