from collections.abc import Generator as GenABC

import pytest
from fiber.pipeline.task.utils.functools import invoke_as_generator


def test_invoke_as_generator_with_ret_func():
    obj = object()

    def simple_func():
        return obj

    output = invoke_as_generator(lambda: simple_func())

    assert isinstance(output, GenABC)
    assert next(output) is obj

    with pytest.raises(StopIteration):
        next(output)


def test_invoke_as_generator_with_yield_func():
    obj1 = object()
    obj2 = object()

    def simple_func():
        yield obj1
        yield obj2

    output = invoke_as_generator(lambda: simple_func())

    assert isinstance(output, GenABC)
    assert next(output) is obj1
    assert next(output) is obj2

    with pytest.raises(StopIteration):
        next(output)
