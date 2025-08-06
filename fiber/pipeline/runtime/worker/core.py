from fiber.pipeline.task import TaskDone, TaskRuntimeError
from fiber.pipeline.runtime.deque.enviroment import DequeEnviroment
from fiber.pipeline.runtime.worker.logging import get_worker_logger


class TaskWorker:
    """
    Воркер для многопоточной обработки Task().
    """

    def __init__(self, deque_environ: DequeEnviroment):
        """
        Создает воркера для многопоточной обработки Task().

        Args:
            deque_environ: Контекст управляющий очередью в котором будет работать воркер (см. подробнее в доках к DequeContext).
        """
        self._deque_enviroment = deque_environ
        self._deque = deque_environ.get_deque()
        self._logger = get_worker_logger()

    def run(self) -> None:
        """
        Запускает воркера (придназнаено для запуска в Thread(target=)).
        """
        self._logger.debug("Запущен.")
        while True:
            item = self._deque.getleft()

            if item is None:
                self._logger.debug("Остановлен.")
                break

            task = item

            generation_lim = self._deque_enviroment.get_generation_limit()
            self._logger.debug(
                f"Начал выполнение Task. Лимит генерации: {generation_lim}"
            )

            for _ in range(generation_lim):
                try:
                    next_task = task.step()
                except TaskDone:
                    self._logger.debug("Завершил выполнение Task.")
                    break
                except TaskRuntimeError:
                    self._logger.critical(
                        "Ошибка во время исполнения. Сломаный Task отброшен."
                    )
                    break

                self._deque.put(next_task)
                self._logger.debug("Добавил в очередь новый Task.")

            if not task.is_done():
                self._deque.put(task)
                self._logger.debug("Вернул Task в очередь.")

            self._deque.task_done()
