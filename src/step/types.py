import src.logman as lm

from src.step.core import Step
from src.step.vars import I, O
from logging import Logger
from typing import Type, Tuple, Any, get_origin, get_args


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
    if not issubclass(step, Step):
        error_mes = f"Шаг {step.__name__} не являеться наследником Step."
        logger.fatal(error_mes, exc_info=True)
        raise TypeError(error_mes)

    bases = getattr(step, "__orig_bases__", [])
    for base_cls in bases:
        if get_origin(base_cls) is Step:
            args = get_args(base_cls)
            if len(args) != 2:
                error_mes = (
                    f"Step должен иметь ровно два параметра типов, но получено: {args}"
                )
                logger.fatal(error_mes)
                raise TypeError(error_mes)

            return args

    error_mes = (
        f"При наследовании от Step у {step.__name__} не указаны параметры типа [I, O]."
    )
    logger.fatal(error_mes, exc_info=True)
    raise TypeError(error_mes)
