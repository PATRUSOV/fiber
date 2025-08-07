from typing import Sequence, Type
from types import NoneType

from fiber.step import Step, get_step_types
from fiber.pipeline.task.builder.validation.rules.base import (
    StepSequenceValidationRule,
    StepSequenceValidationError,
)


class InvalidPipelineEndpointsError(StepSequenceValidationError):
    """Первый шаг должен принимать None, а последний возвращать."""


class EndPointsRule(StepSequenceValidationRule):
    @classmethod
    def check(cls, steps: Sequence[Type[Step]]) -> None:
        """
        Проверяет что первый шаг принимает None, а последний возвращает.
        """
        magic_type = NoneType
        start_step, final_step = steps[0], steps[-1]

        # первый шаг
        start_in, _ = get_step_types(start_step)
        if start_in is not magic_type:
            raise InvalidPipelineEndpointsError(
                f"Нарушен контракт: первый шаг должен принимать {magic_type}, а не {start_in}"
            )

        # последний шаг
        _, final_out = get_step_types(final_step)
        if final_out is not magic_type:
            raise InvalidPipelineEndpointsError(
                f"Нарушен контракт: последний шаг должен возвращать {magic_type}, а не {final_out}"
            )
