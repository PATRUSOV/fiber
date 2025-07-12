from logging import Logger
from typing import Any, Type


def impr_isinstance(
    data: Any, expected_type: Type[Any], error_msg: str, logger: Logger
) -> None:
    """
    Выполняет проверку типа на принадлежность типу. При ошибке логгирует и выбрасывает исключение.
    Особенности:
        +data = None, expected_type = None => True
        +data = ..., expected_type = Any => True

    Args:
        data (Any): Проверяемое значение.
        expected_type (Type[Any]): Ожидаемый тип, извлечённый из Step.
        error_msg (str): сообщение выводимое при ошибке.
        logger (Logger): Обект логгера для соообщения об ошибке.

    Raises:
        TypeError: если тип `data` не соответствует ожидаемому.
    """
    if expected_type is not Any and not isinstance(data, (type(None), expected_type)):
        logger.fatal(error_msg)
        raise TypeError(error_msg)
