from typing import Callable, Generator, TypeVar
from collections.abc import Generator as GenABC


O = TypeVar("O")


def invoke_as_generator(callable: Callable[[], O]) -> Generator[O, None, None]:
    output = callable()

    if isinstance(output, GenABC):
        generator = output
        yield from generator
    else:
        yield output
