from typing import Sequence, Type
from types import NoneType

from fiber.step import Step, get_step_types
from fiber.pipeline.task.builder.exceptions import (
    IncompatibleStepTypesError,
    InvalidPipelineEndpointsError,
    SequenceIsEmpty,
)


class StepSequenceValidator:
    """
    Проверяет корректность последовательности шагов пайплайна.
    """

    @classmethod
    def validate(cls, steps: Sequence[Type[Step]]) -> None:
        """
        Валидирует полную последовательность шагов.
        """
        cls._check_sequence_not_empty(steps)
        cls._validate_type_compatibility(steps)
        cls._validate_endpoints_contract(steps)

    @classmethod
    def _check_sequence_not_empty(cls, steps: Sequence[Type[Step]]):
        if len(steps) == 0:
            raise SequenceIsEmpty

    @classmethod
    def _validate_type_compatibility(cls, steps: Sequence[Type[Step]]) -> None:
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

    @classmethod
    def _validate_endpoints_contract(cls, steps: Sequence[Type[Step]]) -> None:
        """
        Проверяет что первый шаг принимает None, а последний возвращает None.
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
