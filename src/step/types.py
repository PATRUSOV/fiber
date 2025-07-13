import src.logging_manager as lm

from logging import Logger
from typing import Type, Tuple, Any, TypeVar, Final, get_origin, get_args
from src.step.core import Step


I: Final = TypeVar("I")
O: Final = TypeVar("O")


def get_step_types(
    step: Type[Step[I, O]], logger: Logger = lm.get_kernel_logger()
) -> Tuple[Type[Any], Type[Any]]:
    """
    Возвращает входной и выходной тип шага.

    Arguments:
        step: Шаг.
        logger: Логер используемый функцией, по умолчанию - логгер ядра фрейморка.

    Returns:
        Кортеж из типа входных данных и типа выходных данных.
    """
    if issubclass(step, Step):
        bases = getattr(step, "__orig_bases__", [])
        for base_cls in bases:
            if get_origin(base_cls) is Step:
                input_type, output_type = get_args(base_cls)
                return input_type, output_type

    error_mes = f"Шаг {step.__name__} не являеться наследником Step"
    logger.fatal(error_mes)
    raise TypeError(error_mes)
