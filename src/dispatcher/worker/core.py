from src.dispatcher.task import TaskDone
from src.dispatcher.worker.context import WorkerContext


class Worker:
    """
    Воркер для многопоточной обработки Task().
    """

    def __init__(self, context: WorkerContext):
        """
        Создает воркера для многопоточной обработки Task().

        Args:
            context: Контекст в котором будет работать воркер (см. подробнее в доках к WorkerContext).
        """
        self._context = context
        self._context.logger.debug("Создан.")

    def run(self) -> None:
        """
        Запускает воркера (придназнаено для запуска в Thread(target=)).
        """
        self._context.logger.debug("Запущен.")
        while True:
            item = self._context.deque.get()
            if item is None:
                self._context.logger.debug("Остановлен.")
                break
            task = item

            generation_lim = self._context.get_generation_limit()
            self._context.logger.debug(
                f"Начал выполнение Task. Лимит генерации: {generation_lim}"
            )
            for _ in range(generation_lim):
                try:
                    next_task = task.step()
                except TaskDone:
                    self._context.logger.debug("Завершил выполнение Task.")
                    break

                self._context.deque.put(next_task)
                self._context.logger.debug("Добавил в очередь новый Task.")

            if not task.is_done():
                self._context.deque.lput(task)
                self._context.logger.debug("Вернул Task в очередь.")

            self._context.deque.task_done()
