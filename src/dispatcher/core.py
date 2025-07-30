from threading import Thread
from typing import Sequence, Type

import src.logman as lm
from src.collections import ThreadSafeDeque, get_call_head
from src.dispatcher.config import DispatcherConfig
from src.dispatcher.task import Task
from src.dispatcher.worker import Worker, WorkerContext
from src.step import Step


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

        self._logger = lm.get_kernel_logger()
        self._config = config
        self._tdeque: ThreadSafeDeque[Task | None] = ThreadSafeDeque()

        self._logger.debug("Создан Dispatcher.")

        # компиляциия в CallNode-ы и загрузка очереди ими.
        for steps in step_puls:
            call_ll_head = get_call_head(steps)
            task = Task(call_ll_head, None)
            self._tdeque.put(task)
        self._logger.debug("Step успешно преобразованы в Task-и.")

    def run(self) -> None:
        """
        Запускает обработку шагов.
        """
        threads = []

        workers = self._config.WORKERS
        self._logger.debug("Создание Worker-ов...")
        for _ in range(workers):
            context = WorkerContext(
                deque=self._tdeque,
                deque_limit=self._config.TASK_LIMIT,
                max_tasks_per_iter=self._config.TASKS_PER_ITER,
            )
            worker = Worker(context)
            thread = Thread(target=worker.run)
            thread.start()
            threads.append(thread)
            self._logger.debug("Воркеры успешно созданы.")

        self._tdeque.join()
        self._logger.debug("Все Task-и выполнены. Очередь пуста.")

        self._logger.debug("Остановка Worker-ов...")
        for _ in range(len(threads)):
            self._tdeque.put(None)

        for thread in threads:
            thread.join()
        self._logger.debug("Worker-ы остановлены.")
