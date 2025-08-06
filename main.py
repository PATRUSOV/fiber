from typing import Generator
from fiber import Pipeliner, RuntimeConfig, Step


class Calculator(Step[None, int]):
    @classmethod
    def start(cls, data: None) -> Generator[int, None, None]:
        for i in range(5):
            yield i


class NumPrinter(Step[int, None]):
    @classmethod
    def start(cls, data: int) -> None:
        print(data)


Pipeliner(
    runtime_config=RuntimeConfig(
        WORKERS=1,
        TASKS_PER_ITER=5,
        TASK_LIMIT=100,
    ),
).add_pipeline([Calculator, NumPrinter]).run()
