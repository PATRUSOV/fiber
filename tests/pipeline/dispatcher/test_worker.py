import pytest
from threading import Thread

from fiber.step import Step
from fiber.pipeline.task import Task, TaskBuilder
from fiber.pipeline.runtime.deque.enviroment import DequeEnviroment
from fiber.pipeline.runtime.worker import TaskWorker


@pytest.fixture
def valid_ret_task():
    class StartStep(Step[None, int]):
        @classmethod
        def start(cls, data: None) -> int:
            return 42

    class FinishStep(Step[int, None]):
        @classmethod
        def start(cls, data: int) -> None:
            assert data == 42

    task = TaskBuilder.build_from(
        [StartStep, FinishStep],
        strict_building_types=True,
        strict_runtime_types=False,
    )

    return task


def test_worker(valid_ret_task: Task):
    deque_environ = DequeEnviroment(5, 100)
    deque = deque_environ.get_deque()
    deque.put(valid_ret_task)

    worker = TaskWorker(deque_environ)
    worker_thread = Thread(target=worker.run)
    worker_thread.start()

    deque.join()
    deque.put(None)

    worker_thread.join()
