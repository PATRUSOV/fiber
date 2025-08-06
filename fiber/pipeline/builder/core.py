from typing import Sequence, Type

from fiber.step import Step
from fiber.logging import get_kernel_logger
from fiber.pipeline.task import TaskBuilder, TaskBuildError
from fiber.pipeline.runtime.tasks_provider import _HasTasks
from fiber.pipeline.builder.exceptions import PipelineBuildError


class PipelineBuilder(_HasTasks):
    def __init__(self) -> None:
        self._logger = get_kernel_logger().getChild("builder")
        self.__tasks_for_provider__ = []

    def add_pipeline(self, steps: Sequence[Type[Step]]) -> None:
        try:
            task = TaskBuilder.build_from(
                steps,
                strict_building_types=True,
                strict_runtime_types=False,
            )
        except TaskBuildError as e:
            self._logger.fatal(e, exc_info=True)
            raise PipelineBuildError(f"Ошибка сборки конвеера: {e}") from e

        self.__tasks_for_provider__.append(task)
