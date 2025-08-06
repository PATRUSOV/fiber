class TaskDone(Exception):
    """Сигнал завершения Task."""


class TaskRuntimeError(Exception):
    """Ошибка во время исполнения Task."""


class TaskTypeRuntimeError(TaskRuntimeError):
    """Ошибка типов входных / выходных данных Task."""
