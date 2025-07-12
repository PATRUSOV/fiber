import logging
from logging import Logger

from src import __appname__


class LoggingManager:
    @classmethod
    def get_main_logger(cls) -> Logger:
        return logging.getLogger(__appname__)

    @classmethod
    def get_main_module_logger(cls) -> Logger:
        return cls.get_main_logger().getChild("module")

    @classmethod
    def get_kernel_logger(cls) -> Logger:
        main_logger = cls.get_main_logger()
        return main_logger.getChild("kernel")

    @classmethod
    def get_module_logger(cls, module_name: str) -> Logger:
        return cls.get_main_module_logger().getChild(module_name)
