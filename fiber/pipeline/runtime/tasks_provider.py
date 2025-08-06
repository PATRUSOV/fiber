from abc import ABC, abstractmethod
from typing import List, Protocol, Sequence, override

from fiber.pipeline.task.core import Task


class ITaskProvider(ABC):
    @abstractmethod
    def get_tasks(self) -> Sequence[Task]: ...


class _HasTasks(Protocol):
    __tasks_for_provider__: List[Task] = []


class TaskProvider(ITaskProvider):
    def __init__(self, has_tasks: _HasTasks) -> None:
        self._has_tasks = has_tasks

    @override
    def get_tasks(self) -> List[Task]:
        return self._has_tasks.__tasks_for_provider__
