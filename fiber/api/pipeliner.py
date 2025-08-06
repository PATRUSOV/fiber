from typing import Sequence, Type
from fiber.pipeline.builder import PipelineBuilder
from fiber.pipeline.runtime import Runtime, RuntimeConfig, TaskProvider
from fiber.step.core import Step


class Pipeliner:
    def __init__(self, runtime_config: RuntimeConfig) -> None:
        self._runtime_config = runtime_config
        self._pipeline_builder = PipelineBuilder()

    def add_pipeline(self, steps: Sequence[Type[Step]]):
        self._pipeline_builder.add_pipeline(steps)
        return self

    def run(self) -> None:
        dispatcher = Runtime(
            tasks_provider=TaskProvider(self._pipeline_builder),
            config=self._runtime_config,
        ).run()
