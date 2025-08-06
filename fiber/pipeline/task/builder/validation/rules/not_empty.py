from typing import Sequence, Type

from fiber.step import Step
from fiber.pipeline.task.builder.validation.rules.base import (
    StepSequenceValidationRule,
    StepSequenceValidationError,
)


class EmptySequenceError(StepSequenceValidationError):
    """Первый шаг должен принимать None, а последний возвращать."""


class NotEmptySequenceRule(StepSequenceValidationRule):
    @classmethod
    def check(cls, steps: Sequence[Type[Step]]) -> None:
        if len(steps) == 0:
            raise EmptySequenceError()
