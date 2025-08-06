from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    """
    Конфигуратор для Dispatcher.

    Attrs:
        TASK_LIMIT: Максимально допустимое количество активных задач.
        WORKERS: Количество обработчиков (потоков). (Если в цепочке не надо ничего параллелить, то рекомендуется поставить 1.
        TASKS_PER_ITER: Максимум генерируемых Worker-ом задач, за одно обращение к очереди.
    """

    TASK_LIMIT: int
    WORKERS: int
    TASKS_PER_ITER: int
