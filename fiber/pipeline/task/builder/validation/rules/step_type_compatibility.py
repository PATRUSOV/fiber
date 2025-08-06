from typing import Sequence, Type

from fiber.step import Step, get_step_types
from fiber.pipeline.task.builder.validation.rules.base import (
    StepSequenceValidationRule,
    StepSequenceValidationError,
)


class IncompatibleStepTypesError(StepSequenceValidationError):
    """Возвращаемый тип первого шага не совпадает с принимаемым типом второго."""


class StepTypeCompatibilityRule(StepSequenceValidationRule):
    @classmethod
    def check(cls, steps: Sequence[Type[Step]]) -> None:
        for i in range(len(steps) - 1):
            f_step, s_step = steps[i], steps[i + 1]
            cls._check_step_pair(f_step, s_step)

    @classmethod
    def _check_step_pair(cls, f_step: Type[Step], s_step: Type[Step]) -> None:
        """
        Проверяет совместимость выходного типа одного шага и входного типа следующего.
        """
        _, f_out = get_step_types(f_step)
        s_in, _ = get_step_types(s_step)

        if f_out != s_in:
            err_msg = (
                f"Шаги {f_step.__name__} и {s_step.__name__} не совместимы. "
                f"Тип вывода: {f_out}, тип входа следующего шага: {s_in}"
            )
            raise IncompatibleStepTypesError(err_msg)
