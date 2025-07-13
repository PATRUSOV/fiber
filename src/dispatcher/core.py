from typing import Type, Tuple
from queue import Queue
from threading import Thread

from src.step import Step
from src.collections import get_call_head
import src.logging_manager as lm
from src.dispatcher.configurator import DispatcherConfigurator
from src.dispatcher.task import Task, TaskDone


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
        # голова связного списка (call linked list head)
        self._call_ll_head = get_call_head(steps)
        self._configurator = configurator
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

        for _ in range(self._configurator.THREADS):
            thread = Thread(target=self._worker)
            thread.start()
            threads.append(thread)

        self._tqueue.join()

        for thread in threads:
            thread.join()
