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

    def run(self) -> None:
        """
        Запускает воркера (придназнаено для запуска в Thread()).
        """
        while True:
            item = self._context.deque.get()
            if item is None:
                break
            task = item

            generation_lim = self._context.get_generation_limit()
            for _ in range(generation_lim):
                try:
                    next_task = task.step()
                except TaskDone:
                    break

                self._context.deque.put(next_task)

            if not task.is_done():
                self._context.deque.lput(task)

            self._context.deque.task_done()
