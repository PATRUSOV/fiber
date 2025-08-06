from typing import Sequence, Type

from fiber.step import Step
from fiber.pipeline.task.builder.validation.rules import (
    StepTypeCompatibilityRule,
    EndPointsRule,
    NotEmptySequenceRule,
)


class StepSequenceValidator:
    """
    Проверяет корректность последовательности шагов пайплайна.
    """

    @staticmethod
    def validate(steps: Sequence[Type[Step]]) -> None:
        validation_rules = (
            NotEmptySequenceRule,
            StepTypeCompatibilityRule,
            EndPointsRule,
        )

        for rule in validation_rules:
            rule.check(steps)
