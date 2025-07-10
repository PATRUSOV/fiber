from dataclasses import dataclass
from typing import Optional, Type, Union, List, Tuple, Generic

from src.step import Step
from src.step.types import I, O


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


# TODO:
#   +Добавить проверкук типов первого и последнего типа.
def get_call_head(steps: Union[List[Type[Step]], Tuple[Type[Step], ...]]) -> CallNode:
    """
    Преобразует [Список, Кортеж] в односвязный список.

    Arguments:
        steps: Кортеж или список с статическими классами реализующими Step.

    Return:
        Голову связного списка.
    """

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
