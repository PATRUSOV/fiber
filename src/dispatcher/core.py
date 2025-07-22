from typing import Type, Sequence
from threading import Thread

import src.logman as lm

from src.step import Step
from src.collections import get_call_head, ThreadSafeDeque
from src.dispatcher.config import DispatcherConfig
from src.dispatcher.task import Task
from src.dispatcher.worker import Worker, WorkerContext


class Dispatcher:
    """
    Исполняющим ядром для классов реализующих интерфейс Step.
    Отвечает за создание цепочек из Step, и управление многопотоком.
    """

    def __init__(
        self,
        step_puls: Sequence[Sequence[Type[Step]]],
        config: DispatcherConfig = DispatcherConfig(
            TASK_LIMIT=50, WORKERS=4, TASKS_PER_ITER=3
        ),
    ):
        """
        Создает объект-диспетчера для кправления Step-цепочками.

        Args:
            step_puls: Последовательность с последовательностями из шагов.
            config: Объект конфигурации (см. подробнее в его доках).
        """
        # компиляциия в CallNode-ы и загрузка очереди ими.
        for steps in step_puls:
            call_ll_head = get_call_head(steps)
            task = Task(call_ll_head, None)
            self._tdeque.put(task)

        self._config = config
        self._logger = lm.get_kernel_logger()
        self._tdeque: ThreadSafeDeque[Task | None] = ThreadSafeDeque()

    def run(self) -> None:
        """
        Запускает обработку шагов.
        """
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
