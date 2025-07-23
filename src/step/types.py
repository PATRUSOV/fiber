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
    """
    Извлекает параметры типов входа и выхода (I, O) из generic-наследника класса Step.

    Аргументы:
        step (Type[Step]):
            Класс, унаследованный от Step с параметрами типа, например Step[int, str].
            Должен быть прямым наследником Step[...], иначе произойдёт исключение.

        logger (Logger, optional):
            Логгер, используемый для фиксации ошибок. По умолчанию используется логгер ядра.

    Возвращает:
        Tuple[Type[Any], Type[Any]]:
            Кортеж из двух типов — (I, O), где:
                - I — тип входных данных, принимаемых шагом;
                - O — тип выходных данных, возвращаемых шагом.

    Исключения:
        NotAStepError:
            Брошено, если переданный класс не является наследником Step.

        StepTypeParametersMissing:
            Класс унаследован от Step, но параметров типов не указано вообще (Step без [I, O]).

        StepTypeParameterCountMismatch:
            Указано не два параметра типа (например, Step[int], Step[int, str, float]).

        StepTypeExtractionError:
            Step[...] не найден в __orig_bases__, вероятно, скрыт в глубокой иерархии.

    Пример:
        >>> class MyStep(Step[int, str]): ...
        >>> get_step_types(MyStep)
        (<class 'int'>, <class 'str'>)

        >>> class InvalidStep(Step): ...
        >>> get_step_types(InvalidStep)
        # → StepTypeParametersMissing

        >>> class NotAStep: ...
        >>> get_step_types(NotAStep)
        # → NotAStepError
    """
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
