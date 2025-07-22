import logging

from src import __appname__

# TODO:
# + Добавить документация
# + Предоставить удобный апи для настройки логгера.


def get_main_logger() -> logging.Logger:
    """
    Возвращает:
        Логгер для всего приложения.
    """
    return logging.getLogger(__appname__)


def get_main_step_logger() -> logging.Logger:
    """
    Возвращает:
        Базовый логгер для от которого наследуются логгеры для каждого Step.
    """
    return get_main_logger().getChild("step")


def get_kernel_logger() -> logging.Logger:
    """
    Возвращает:
        Логгер используемый "под капотом" у фремворка.
    """
    main_logger = get_main_logger()
    return main_logger.getChild("kernel")
