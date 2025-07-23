import src.logman as lm

from src.step.core import Step
from src.step.vars import I, O
from src.step.exceptions import (
    NotAStepError,
    StepTypeParameterCountMismatch,
    StepTypeParametersMissing,
    StepTypeExtractionError,
)
from logging import Logger
from typing import Type, Tuple, Any, get_origin, get_args


def get_step_types(
    step: Type[Step],
    logger: Logger = lm.get_kernel_logger(),
) -> Tuple[Type[Any], Type[Any]]:
    # простая проверка на наследование от Step
    if not issubclass(step, Step):
        error_msg = f"{step.__name__} не является наследником Step."
        logger.fatal(error_msg)
        raise NotAStepError(error_msg)

    # получение Generic-ов родителей (объектов класса typing._GenericAlias)
    for base in getattr(step, "__orig_bases__", []):
        # получение обекта класса
        if get_origin(base) is Step:
            # получение аргументов Generic-а
            args = get_args(base)

            # проврка на отсутвие арументов
            if len(args) == 0:
                error_msg = f"{step.__name__} унаследован от Step, но параметры типа не указаны."
                logger.fatal(error_msg)
                raise StepTypeParametersMissing(error_msg)

            # проверка на недостаток / избыток аргументов
            if len(args) != 2:
                error_msg = f"{step.__name__} должен наследовать Step с двумя параметрами типа, но получено {len(args)}: {args}"
                logger.fatal(error_msg)
                raise StepTypeParameterCountMismatch(error_msg)

            return args

    # если Step[I, O] вообще не нашёлся
    error_msg = f"{step.__name__} не содержит Step[...] в __orig_bases__ — возможно, Step скрыт в иерархии."
    logger.fatal(error_msg)
    raise StepTypeExtractionError(error_msg)
