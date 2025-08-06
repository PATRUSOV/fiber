from dataclasses import dataclass
from typing import Optional, Generic, Sequence, TypeVar


T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    """
    Лист связного списка. Дополнительно хранит ссылку на следующий лист.
    Если лист является последним, то next = None.

    Attrs:
        item: T
        next: Следующий вызов.
    """

    item: T
    next: Optional["Node[T]"] = None


def get_linked_list_from(sequence: Sequence[T]) -> Node[T]:
    """
    Преобразует последовательность в односвязный список из Node.

    Аргументы:
        steps (Sequence[T]): Последовательность.

    Возвращаает:
        Node[T] - голова связного списка.
    """

    if len(sequence) == 0:
        raise ValueError("Нельзя создать список из пустой последовательности.")

    head_node = Node(sequence[0], None)

    prev_node = head_node

    for item in sequence[1:]:
        new_node = Node(item)

        prev_node.next = new_node
        prev_node = new_node

    return head_node
