from logging import Logger
from typing import Type, Generator, Tuple, Any
from queue import Queue
from threading import Thread

from src.step import Step
from src.collections import get_call_head, CallNode
from src.logging_manager import LoggingManager
from src.dispatcher.configurator import DispatcherConfigurator


class Dispatcher:
    """
    Класс является исполняющим ядром для классов реализующих интерфейс Step.
    """

    def __init__(
        self,
        steps: Tuple[Type[Step], ...],
        configurator: DispatcherConfigurator = DispatcherConfigurator(
            THREADS=1, MAX_TASKS=30
        ),
    ):
        # голова связного списка
        self._call_ll_head = get_call_head(steps)
        self._configurator = configurator
        self._logger = LoggingManager.get_kernel_logger()
        self._call_queue = Queue()

    def _worker(self, call_node: CallNode, data: Any) -> None: ...

    def run(self) -> None: ...
