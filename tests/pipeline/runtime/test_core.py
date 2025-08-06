from typing import List

from fiber.pipeline.task import Task, TaskBuilder
from fiber.step import Step
from fiber.pipeline.runtime import Runtime, RuntimeConfig, ITaskProvider

START_STEP_OK = False
FINISH_STEP_OK = False


class TaskProviderTestingImpl(ITaskProvider):
    def get_tasks(
        self,
    ) -> List[Task]:
        class StartStep(Step[None, int]):
            @classmethod
            def start(cls, data: None) -> int:
                global START_STEP_OK
                START_STEP_OK = True
                return 42

        class FinishStep(Step[int, None]):
            @classmethod
            def start(cls, data: int) -> None:
                assert data == 42
                global FINISH_STEP_OK
                FINISH_STEP_OK = True

        task = TaskBuilder.build_from(
            [StartStep, FinishStep],
            strict_building_types=True,
            strict_runtime_types=False,
        )

        return [task]


def test_dispatcher():
    Runtime(
        tasks_provider=TaskProviderTestingImpl(),
        config=RuntimeConfig(WORKERS=5, TASKS_PER_ITER=5, TASK_LIMIT=100),
    ).run()

    assert START_STEP_OK
    assert FINISH_STEP_OK
