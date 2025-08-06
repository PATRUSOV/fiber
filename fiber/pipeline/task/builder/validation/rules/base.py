from abc import ABC, abstractmethod
from typing import Sequence, Type

from fiber.step import Step


class StepSequenceValidationRule(ABC):
    @classmethod
    @abstractmethod
    def check(cls, steps: Sequence[Type[Step]]): ...


class StepSequenceValidationError(Exception):
    """Ошибка валидации цепочки шагов"""
