import pytest

from fiber.pipeline.runtime.deque.enviroment import DequeEnviroment


@pytest.fixture
def enviroment() -> DequeEnviroment:
    return DequeEnviroment(deque_limit=10, max_tasks_per_iter=5)


def test_generation_lim_at_empty_deque(enviroment: DequeEnviroment):
    assert enviroment.get_generation_limit() == 5


def test_generation_lim_with_five_empty_deque(enviroment: DequeEnviroment):
    deque = enviroment.get_deque()

    for _ in range(5):
        deque.put(None)

    assert enviroment.get_generation_limit() == 3
