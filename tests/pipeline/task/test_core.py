import pytest
from typing import Generator

from fiber.pipeline.task.exceptions import TaskTypeRuntimeError
from fiber.step import Step
from fiber.pipeline.task import Task, TaskDone, TaskBuilder, TaskRuntimeError


def base_task_integriry_checking(task: Task):
    assert isinstance(task, Task)
    assert not task.is_done()


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


def test_start_state_with_single_step():
    class SingleStep(Step[None, None]): ...

    task = TaskBuilder.build_from(
        [SingleStep],
        strict_building_types=True,
        strict_runtime_types=False,
    )
    base_task_integriry_checking(task)


def test_start_state_with_many_steps(valid_ret_task: Task):
    base_task_integriry_checking(valid_ret_task)


def test_raise_task_done(valid_ret_task: Task):
    next_task = valid_ret_task.step()

    with pytest.raises(TaskDone):
        next_task.step()


def test_task_is_done_with_ret(valid_ret_task: Task):
    valid_ret_task.step()

    with pytest.raises(TaskDone):
        valid_ret_task.step()

    assert valid_ret_task.is_done()


@pytest.fixture
def valid_yield_task():
    class StartStep(Step[None, int]):
        @classmethod
        def start(cls, data: None) -> Generator[int, None, None]:
            for i in range(3):
                yield i

    class FinishStep(Step[int, None]):
        num = 0

        @classmethod
        def start(cls, data: int) -> None:
            if data != cls.num:
                assert False
            cls.num += 1

    task = TaskBuilder.build_from(
        [StartStep, FinishStep],
        strict_building_types=True,
        strict_runtime_types=False,
    )
    return task


def test_yield_task(valid_yield_task: Task):
    for _ in range(3):
        task = valid_yield_task.step()

        with pytest.raises(TaskDone):
            task.step()

    with pytest.raises(TaskDone):
        valid_yield_task.step()


def test_task_is_done_with_yield(valid_yield_task: Task):
    for _ in range(3):
        task = valid_yield_task.step()
    with pytest.raises(TaskDone):
        valid_yield_task.step()

    assert valid_yield_task.is_done()


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

    task = TaskBuilder.build_from(
        [StartStep, FinishStep],
        strict_building_types=True,
        strict_runtime_types=False,
    )
    return task


def test_excpetion_between_steps(ret_task_with_exc_at_first_step: Task):
    with pytest.raises(TaskRuntimeError):
        ret_task_with_exc_at_first_step.step()
    assert ret_task_with_exc_at_first_step.is_done()


def test_runtime_type():
    class StartStepLier(Step[None, int]):
        @classmethod
        def start(cls, data: None) -> int:
            return 1

    class SomeStep(Step[int, int]):
        @classmethod
        def start(cls, data: int) -> int:
            return 1

    class FinishStep(Step[int, None]):
        @classmethod
        def start(cls, data: int) -> None:
            return None

    task = TaskBuilder.build_from(
        [StartStepLier, SomeStep, FinishStep],
        strict_building_types=True,
        strict_runtime_types=True,
    )


def test_runtime_type_error():
    class StartStepLier(Step[None, int]):
        @classmethod
        def start(cls, data: None) -> int:
            return "unexpected type"  # type: ignore (специальный тест на некорекные данные)

    class SomeStep(Step[int, int]):
        @classmethod
        def start(cls, data: int) -> int:
            return 1

    class FinishStep(Step[int, None]):
        @classmethod
        def start(cls, data: int) -> None:
            return None

    task = TaskBuilder.build_from(
        [StartStepLier, SomeStep, FinishStep],
        strict_building_types=False,
        strict_runtime_types=True,
    )

    with pytest.raises(TaskTypeRuntimeError):
        task.step()

    assert task.is_done()
