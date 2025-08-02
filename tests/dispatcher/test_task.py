from typing import Generator
import pytest

from fiber.runtime.task import Task, TaskDone
from fiber.step import Step
from fiber.collections import get_call_head


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

    valid_call_ll_head = get_call_head([StartStep, FinishStep])
    task = Task(valid_call_ll_head, None)

    return task


def test_raise_task_done(valid_ret_task: Task):
    next_task = valid_ret_task.step()

    with pytest.raises(TaskDone):
        next_task.step()


def test_task_is_done(valid_ret_task: Task):
    next_task = valid_ret_task.step()

    try:
        valid_ret_task.step()
    except TaskDone:
        ...

    assert valid_ret_task.is_done()


@pytest.fixture
def valid_yield_task():
    class StartStep(Step[None, int]):
        @classmethod
        def start(cls, data: None) -> Generator[int, None, None]:
            for i in range(3):
                yield i

    class FinishStep(Step[int, None]):
        @classmethod
        def start(cls, data: int) -> None:
            if not data < 3:
                assert False

    valid_call_ll_head = get_call_head([StartStep, FinishStep])
    task = Task(valid_call_ll_head, None)

    return task


def test_yield_task(valid_yield_task: Task):
    for _ in range(3):
        task = valid_yield_task.step()

        with pytest.raises(TaskDone):
            task.step()

    with pytest.raises(TaskDone):
        valid_yield_task.step()


class ExpectedExc(Exception): ...


@pytest.fixture
def ret_task_with_exc_at_first_step():
    class StartStep(Step[None, int]):
        @classmethod
        def start(cls, data: None) -> int:
            raise ExpectedExc

    class FinishStep(Step[int, None]):
        @classmethod
        def start(cls, data: int) -> None: ...

    valid_call_ll_head = get_call_head([StartStep, FinishStep])
    task = Task(valid_call_ll_head, None)

    return task


def test_excpetion_between_steps(ret_task_with_exc_at_first_step: Task):
    with pytest.raises(TaskDone):
        ret_task_with_exc_at_first_step.step()
