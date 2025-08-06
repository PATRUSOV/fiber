from fiber.step import Step
from fiber.pipeline.builder import PipelineBuilder
from fiber.pipeline.task import Task


def test_pipeline_builder():
    pipeline_builder = PipelineBuilder()

    class StartStep(Step[None, int]):
        @classmethod
        def start(cls, data: None) -> int:
            return 42

    class FinishStep(Step[int, None]):
        @classmethod
        def start(cls, data: int) -> None:
            assert data == 42

    pipeline_builder.add_pipeline([StartStep, FinishStep])

    task = pipeline_builder.__tasks_for_provider__[0]
    assert isinstance(task, Task)
