from typing import Type, Tuple
from threading import Thread

import src.logging_manager as lm

from src.step import Step
from src.collections import get_call_head, ThreadSafeDeque
from src.dispatcher.configurator import DispatcherConfig
from src.dispatcher.task import Task
from src.dispatcher.worker import Worker, WorkerContext


class Dispatcher:
    """
    Класс является исполняющим ядром для классов реализующих интерфейс Step.
    """

    def __init__(
        self,
        step_puls: Tuple[Tuple[Type[Step], ...], ...],
        config: DispatcherConfig = DispatcherConfig(
            TASK_LIMIT=50, WORKERS=4, TASKS_PER_ITER=3
        ),
    ):
        # голова связного списка (call linked list head)
        self._call_ll_heads = []

        # компиляциия в CallNode-ы
        for steps in step_puls:
            call_linked_list_head = get_call_head(steps)
            self._call_ll_heads.append(call_linked_list_head)

        self._config = config
        self._logger = lm.get_kernel_logger()
        self._tdeque: ThreadSafeDeque[Task | None] = ThreadSafeDeque()

    def run(self) -> None:
        # инициализация очереди
        for call_ll_head in self._call_ll_heads:
            start_task = Task(call_ll_head, None)
            self._tdeque.put(start_task)

        threads = []

        for _ in range(self._config.WORKERS):
            context = WorkerContext(
                deque=self._tdeque,
                deque_limit=self._config.TASK_LIMIT,
                max_tasks_per_iter=self._config.TASKS_PER_ITER,
            )
            worker = Worker(context)
            thread = Thread(target=worker.run)
            thread.start()
            threads.append(thread)

        self._tdeque.join()

        for _ in range(len(threads)):
            self._tdeque.put(None)

        for thread in threads:
            thread.join()
