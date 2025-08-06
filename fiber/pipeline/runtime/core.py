from threading import Thread

from fiber.logging import get_kernel_logger
from fiber.pipeline.runtime.deque.enviroment import DequeEnviroment
from fiber.pipeline.runtime.worker import TaskWorker
from fiber.pipeline.runtime.config import RuntimeConfig
from fiber.pipeline.runtime.tasks_provider import ITaskProvider


class Runtime:
    """
    Исполняющим ядром для классов реализующих интерфейс Step.
    Отвечает за создание цепочек из Step, и управление многопотоком.
    """

    def __init__(self, tasks_provider: ITaskProvider, config: RuntimeConfig):
        """
        Создает объект-диспетчера для управления Step-цепочками.

        Args:
            step_puls: Последовательность с последовательностями из шагов.
            config: Объект конфигурации (см. подробнее в его доках).
        """

        self._logger = get_kernel_logger().getChild("dispatcher")
        self._config = config
        self._deque_environ = DequeEnviroment(
            deque_limit=self._config.TASK_LIMIT,
            max_tasks_per_iter=self._config.TASKS_PER_ITER,
        )

        for task in tasks_provider.get_tasks():
            deque = self._deque_environ.get_deque()
            deque.put(task)

        self._logger.debug("Создан Dispatcher.")

    def run(self) -> None:
        """
        Запускает обработку шагов.
        """
        threads = []

        workers = self._config.WORKERS
        self._logger.info("Создание Worker-ов...")
        for _ in range(workers):
            worker = TaskWorker(self._deque_environ)
            thread = Thread(target=worker.run)
            thread.start()
            threads.append(thread)
        self._logger.debug("Все воркеры успешно созданы и запущены.")

        self._deque_environ.get_deque().join()
        self._logger.info("Все Task-и выполнены. Очередь пуста.")

        self._logger.info("Остановка Worker-ов...")
        deque = self._deque_environ.get_deque()
        for _ in range(len(threads)):
            deque.put(None)

        for thread in threads:
            thread.join()
        self._logger.info("Worker-ы остановлены.")
