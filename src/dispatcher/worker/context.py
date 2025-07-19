from src.collections import ThreadSafeDeque
from src.dispatcher.worker.logr import get_worker_logger
from src.dispatcher.task import Task


class WorkerContext:
    """
    Контекст для Worker. Расчитывает лимит генерации и хранит данные необходимые Worker.
    """

    def __init__(
        self,
        deque: ThreadSafeDeque[Task | None],
        deque_limit: int,
        max_tasks_per_iter: int,
    ):
        """
        Создает контекст для исполнения Worker.

        Args:
            deque: Двустороння очередь с которой будет работать Worker.
            deque_limit: Предел к которому стремиться размер очереди (при приближении к нему генерация замедляется).
            max_task_per_iter: Максимальное колиство задач которые воркер может сгенерировать за одно обращение к очереди.
        """
        self.deque = deque
        self.logger = get_worker_logger()
        self._deque_limit = deque_limit
        self._max_tasks_per_iter = max_tasks_per_iter

    def get_generation_limit(self) -> int:
        """
        Вычисляет количесво задач которые воркер сможет сгенерировать за одно обращение к очереди.
        """
        queue_size = len(self.deque)
        deque_lim = self._deque_limit
        max_task_per_iter = self._max_tasks_per_iter
        usage = queue_size / deque_lim
        raw_tasks = round(max_task_per_iter * (1 - usage))
        return max(1, raw_tasks)
