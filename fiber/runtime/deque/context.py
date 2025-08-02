from tsdeque import ThreadSafeDeque

from fiber.utils.math.round import roundu


class DequeContext:
    """
    Контекст для Deque. Расчитывает лимит генераци.
    """

    def __init__(
        self,
        deque: ThreadSafeDeque,
        deque_limit: int,
        max_tasks_per_iter: int,
    ):
        """
        Создает контекст для исполнения Worker.

        Args:
            deque: Двустороння очередь.
            deque_limit: Предел к которому стремиться размер очереди (при приближении к нему генерация замедляется).
            max_task_per_iter: Максимальное колиство задач которые воркер может сгенерировать за одно обращение к очереди.
        """
        self._deque = deque
        self._deque_limit = deque_limit
        self._max_tasks_per_iter = max_tasks_per_iter

    def get_deque(self) -> ThreadSafeDeque:
        return self._deque

    def get_generation_limit(self) -> int:
        """
        Вычисляет количесво задач которые воркер сможет сгенерировать за одно обращение к очереди.
        """
        queue_size = len(self._deque)
        deque_lim = self._deque_limit
        max_task_per_iter = self._max_tasks_per_iter

        usage = queue_size / deque_lim
        raw_tasks = roundu(max_task_per_iter * (1 - usage))

        return max(1, raw_tasks)
