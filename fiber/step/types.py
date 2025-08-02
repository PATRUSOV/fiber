from logging import Logger
from typing import Type, Tuple, Any, get_origin, get_args

from fiber.logging import get_kernel_logger
from fiber.step.core import Step
from fiber.step.exceptions import NotAStepError, StepTypeParametersMissing


def get_step_types(
    step: Type[Step],
    logger: Logger = get_kernel_logger(),
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
            Если переданный класс не является наследником Step.

    Пример:
        >>> class MyStep(Step[int, str]): ...
        >>> get_step_types(MyStep)
        (<class 'int'>, <class 'str'>)

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

            return args

    error_msg = f"{step.__name__} должен явно указывать параметры типа: Step[InputType, OutputType]"
    step.logger.fatal(error_msg)
    raise StepTypeParametersMissing(error_msg)
