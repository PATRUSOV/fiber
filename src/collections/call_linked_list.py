from dataclasses import dataclass
from logging import Logger
from types import NoneType
from typing import Optional, Type, Generic, Sequence

from src.step import Step
from src.step.types import get_step_types
from src.step.vars import I, O
from src.collections.exceptions import IncompatibleStepTypesError

import src.logman as lm


@dataclass
class CallNode(Generic[I, O]):
    """
    Класс вызова, содержит данные текущего вызова то есть статический класс реализующий Step.
    Дополнительно хранит ссылку на следующий вызов. Если верщина являетьяс последней, то next = None.

    Attrs:
        step: Статический класс реализующий Step.
        next: Следующий вызов.
    """

    step: Type[Step[I, O]]
    next: Optional["CallNode"]


def get_call_head(
    steps: Sequence[Type[Step]], logger: Logger = lm.get_kernel_logger()
) -> CallNode:
    """
    Преобразует последовательность из Type[Step] в односвязный список из CallNode.

    Аргументы:
        steps (Sequence[Type[Step]]]): Последовательность из статических классов реализующих Step.
        logger (Logger): Логгер используемый функцией.

    Возвращаает:
        CallNode - голова связного списка.
    """
    _check_first_and_last_steps_conract(steps, logger)

    if len(steps) == 0:
        err_msg = "Нельзя создать список из пустой последовательности."
        logger.fatal(err_msg, exc_info=True)
        raise ValueError(err_msg)

    head_node = CallNode(steps[0], None)

    prev_node = head_node

    for i in range(1, len(steps)):
        step = steps[i]

        node = CallNode(step, None)

        _static_type_check_between_two_steps(prev_node.step, node.step, logger)

        prev_node.next = node
        prev_node = node

    return head_node


def _static_type_check_between_two_steps(
    f_step: Type[Step],
    s_step: Type[Step],
    logger: Logger,
):
    """
    Выполняет статическую проверку совместимости типов между двумя шагами исполнения.

    Проверяется, что возвращаемый тип (O) первого шага `f_step` совпадает с
    типом входных данных (I) второго шага `s_step`, в соответствии с декларацией
    типов при наследовании от `Step[I, O]`.

    Аргументы:
        f_step (Type[Step]): Первый шаг.
        s_step (Type[Step]): Второй шаг.
        logger (Logger): Логгер для регистрации ошибок и отладочной информации.

    Исключения:
        IncompatibleStepTypesError: Если возвращаемый тип `f_step` не совпадает с принимаемым типом `s_step`.
    """
    _, f_out = get_step_types(f_step)
    s_in, _ = get_step_types(s_step)

    if f_out is not s_in:
        err_msg = f"Шаги {f_step.__name__} и {s_step.__name__} не совместимы. Возвращаемый тип первого шага: {f_out}, а принимаемый вторго {s_in}"
        logger.fatal(err_msg, exc_info=True)
        raise IncompatibleStepTypesError(err_msg)


def _check_first_and_last_steps_conract(
    steps: Sequence[Type[Step]],
    logger: Logger,
) -> None:
    """
    Проверяет что первый и последний элеметы групы соответсвуют guideline:
    первый принимимает None, а последний возвращает None.

    Аргументы:
        steps (Sequence[Type[Step]]]): Последовательность из статических классов реализующих Step.
        logger (Logger): Логгер используемый функцией.

    Исключения:
        TypeError: Если шаг нарушил конракт.
    """
    # ожидаемый тип, фактически заглушка
    magic_type = NoneType
    base_err_msg = "Нарушен контракт: "
    start_step, final_step = steps[0], steps[-1]

    # проверка входного типа в первом шаге
    start_step_inp_type = get_step_types(start_step)[0]
    if start_step_inp_type is not magic_type:
        err_msg = (
            base_err_msg
            + f"Тип принимаемых данных в первом шаге должен быть {magic_type}. Текущий тип: {start_step_inp_type}."
        )
        logger.fatal(err_msg, exc_info=True)
        raise TypeError(err_msg)

    # проверка возвращаемого значения в последем шаге
    final_step_outp_type = get_step_types(final_step)[1]
    if final_step_outp_type is not magic_type:
        err_msg = (
            base_err_msg
            + f"Тип вовращаемых данных в последнем шаге должен быть {magic_type}. Текущий тип: {final_step_outp_type}."
        )
        logger.fatal(err_msg, exc_info=True)
        raise TypeError(err_msg)
