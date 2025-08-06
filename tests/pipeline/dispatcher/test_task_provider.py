from fiber.pipeline.runtime.tasks_provider import TaskProvider, _HasTasks


def test_task_provider():
    obj0, obj1 = object(), object()

    class HasTaskTestingImpl(_HasTasks):
        def __init__(self):
            self.__tasks_for_provider__ = [obj0, obj1]  # type: ignore

    objs = TaskProvider(HasTaskTestingImpl()).get_tasks()

    assert objs[0] is obj0 and objs[1] is obj1

