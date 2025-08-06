from typing import Sequence, Type

from fiber.step import Step
from fiber.pipeline.task.core import Task
from fiber.pipeline.task.utils.datastructs import get_linked_list_from
from fiber.pipeline.task.builder.validation import StepSequenceValidator


class TaskBuilder:
    @staticmethod
    def build_from(
        steps: Sequence[Type[Step]],
        strict_building_types: bool,
        strict_runtime_types: bool,
    ) -> Task:
        if strict_building_types:
            StepSequenceValidator.validate(steps)

        call_linked_list_head = get_linked_list_from(steps)
        task = Task(
            call_node=call_linked_list_head,
            payload=None,
            strict_types=strict_runtime_types,
        )

        return task
