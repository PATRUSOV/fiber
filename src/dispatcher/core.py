from typing import Type, Tuple
from queue import Queue
from threading import Thread

import src.logging_manager as lm

from src.step import Step
from src.collections import get_call_head
from src.dispatcher.configurator import DispatcherConfig
from src.dispatcher.task import Task, TaskDone


class Dispatcher:
    """
    Класс является исполняющим ядром для классов реализующих интерфейс Step.
    """

    def __init__(
        self,
        steps: Tuple[Type[Step], ...],
        config: DispatcherConfig = DispatcherConfig(
            TASK_LIMIT=50, WORKERS=4, TASKS_PER_ITER=3
        ),
    ):
        # голова связного списка (call linked list head)
        self._call_ll_head = get_call_head(steps)
        self._config = config
        self._logger = lm.get_kernel_logger()
        self._tqueue: Queue[Task] = Queue()

    def _worker(self) -> None:
        while True:
            task = self._tqueue.get()

            while True:
                try:
                    outp = task.step()
                except TaskDone:
                    break

                self._tqueue.put(outp)

            self._tqueue.task_done()

    def run(self) -> None:
        # инициализация очереди
        start_task = Task(self._call_ll_head, None)
        self._tqueue.put(start_task)

        threads = []

        for _ in range(self._config.WORKERS):
            thread = Thread(target=self._worker)
            thread.start()
            threads.append(thread)

        self._tqueue.join()

        for thread in threads:
            thread.join()
