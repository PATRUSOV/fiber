import logging

from src import __appname__

# TODO:
# + Добавить документация
# + Предоставить удобный апи для настройки логгера.


def get_main_logger() -> logging.Logger:
    return logging.getLogger(__appname__)


def get_main_module_logger() -> logging.Logger:
    return get_main_logger().getChild("module")


def get_kernel_logger() -> logging.Logger:
    main_logger = get_main_logger()
    return main_logger.getChild("kernel")


def get_module_logger(module_name: str) -> logging.Logger:
    return get_main_module_logger().getChild(module_name)
