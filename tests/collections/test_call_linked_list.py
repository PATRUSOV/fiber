import pytest

from fiber.collections import get_call_head, IncompatibleStepTypesError
from fiber.step import Step


class StartStep(Step[None, int]): ...


class FinalStep(Step[int, None]): ...


class IncStep(Step[int, str]): ...


@pytest.fixture
def valid_call_ll_head():
    return get_call_head((StartStep, FinalStep))


def test_compile_from_step_to_call_node(valid_call_ll_head):
    assert valid_call_ll_head.step is StartStep
    assert valid_call_ll_head.next.step is FinalStep


def test_final_node(valid_call_ll_head):
    assert valid_call_ll_head.next.next is None


def test_incorrect_start_type():
    with pytest.raises(IncompatibleStepTypesError):
        get_call_head([IncStep, FinalStep])


def test_incorrect_final_type():
    with pytest.raises(IncompatibleStepTypesError):
        get_call_head([StartStep, IncStep])


def test_single_node():
    class SingleStep(Step[None, None]): ...

    call_node = get_call_head([SingleStep])
    assert call_node.step is SingleStep
    assert call_node.next is None
