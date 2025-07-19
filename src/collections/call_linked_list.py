from dataclasses import dataclass
from logging import Logger
from typing import Optional, Type, Generic, Sequence

from src.step import Step
from src.step.types import I, O, get_step_types
import src.logging_manager as lm


@dataclass
class CallNode(Generic[I, O]):
    """
    Класс вызова, содержит данные текущего вызова то есть статический класс реализующий Step.
    Дополнительно хранит ссылку на следующий вызов. Если верщина являетьяс последней, то next = None.

    Attributes:
        step: Статический класс реализующий Step.
        next: Следующий вызов.
    """

    step: Type[Step[I, O]]
    next: Optional["CallNode"]


def get_call_head(steps: Sequence[Type[Step]]) -> CallNode:
    """
    Преобразует [Список, Кортеж] в односвязный список.

    Arguments:
        steps: Кортеж или список с статическими классами реализующими Step.

    Return:
        Голову связного списка.
    """
    _check_first_and_last_steps_conract(steps)

    if len(steps) == 0:
        raise ValueError("Нельзя создать список из пустого кортежа")

    head_node = CallNode(steps[0], None)

    node = head_node

    for i in range(1, len(steps)):
        cls = steps[i]
        next_node = CallNode(cls, None)
        node.next = next_node
        node = next_node

    return head_node


def _check_first_and_last_steps_conract(
    steps: Sequence[Type[Step]],
    logger: Logger = lm.get_kernel_logger(),
) -> None:
    """
    Проверяет что первый и последний элеметы групы соответсвуют guidline:
    первый принимимает None, а последний возвращает None.

    Arguments:
        steps: Цепочка шагов.

    Raises:
        TypeError: Если шаг нарушил конракт.
    """
    # ожидаемый тип, фактически заглушка
    magic_type = None
    base_err_msg = "Нарушен контракт: "
    start_step, final_step = steps[0], steps[-1]

    # проверка входного типа в первом шаге
    start_step_inp_type = get_step_types(start_step)[0]
    if start_step_inp_type is not magic_type:
        err_msg = (
            base_err_msg
            + f"Тип принимаемых данных в первом шаге должен быть {magic_type}. Текущий тип: {start_step_inp_type}."
        )
        logger.fatal(err_msg)
        raise TypeError(err_msg)

    # проверка возвращаемого значения в последем шаге
    final_step_outp_type = get_step_types(final_step)[1]
    if final_step_outp_type is not magic_type:
        err_msg = (
            base_err_msg
            + f"Тип вовращаемых данных в последнем шаге должен быть {magic_type}. Текущий тип: {start_step_inp_type}."
        )
        logger.fatal(err_msg)
        raise TypeError(err_msg)
