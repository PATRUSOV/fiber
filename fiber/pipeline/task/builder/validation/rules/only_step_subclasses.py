from typing import Sequence, Type

from fiber.step import Step
from fiber.pipeline.task.builder.validation.rules.base import (
    StepSequenceValidationRule,
    StepSequenceValidationError,
)


class NotAStepError(StepSequenceValidationError):
    """Каждый шаг должен быть наследником Step."""


class OnlyStepSubclassesRule(StepSequenceValidationRule):
    @classmethod
    def check(cls, steps: Sequence[Type[Step]]) -> None:
        for step in steps:
            if not issubclass(step, Step):
                raise NotAStepError("Каждый шаг должен быть наследником Step.")
