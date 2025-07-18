from dataclasses import dataclass


@dataclass
class DispatcherConfig:
    TASK_LIMIT: int
    WORKERS: int
    TASKS_PER_ITER: int
