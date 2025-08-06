from typing import Any, Type, TypeVar, Union

T = TypeVar("T")


def impr_isinstance(data: T, expected_type: Union[Type[T], Any]) -> bool:
    """
    Выполняет проверку типа на принадлежность типу.

    Особенности:
        `data` = ..., `expected_type` = typing.Any => True

    Параметры:
        `data` (Any): Проверяемое значение.
        `expected_type` (Type[Any]): Ожидаемый тип, извлечённый из Step.
    """
    if expected_type is Any:
        return True

    if isinstance(data, expected_type):
        return True

    return False
