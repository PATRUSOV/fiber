from typing import Dict, List, Set, Any

import pytest
from fiber.pipeline.task.utils.types import impr_isinstance


@pytest.mark.parametrize(
    ["obj", "obj_t"],
    [
        (1, int),
        (1.1, float),
        ("1", str),
    ],
)
def test_with_primitevs(obj, obj_t):  # FIX: проверить название
    assert impr_isinstance(obj, obj_t)


@pytest.mark.parametrize(
    ["obj", "obj_t"],
    [
        (list(), List),
        (dict(), Dict),
        (set(), Set),
    ],
)
def test_with_empty_collections(obj, obj_t):
    assert impr_isinstance(obj, obj_t)


@pytest.mark.parametrize(
    ["obj", "obj_t"],
    [
        ([1, 2], List),
        ({"field": 1}, Dict),
        ({1, 2}, Set),
    ],
)
def test_with_non_empty_collections_generics(obj, obj_t):
    assert impr_isinstance(obj, obj_t)


def test_with_any():
    assert impr_isinstance(1, Any)


def test_incorret_type():
    assert not impr_isinstance(1, str)


# FIXME: Написать алгоритм проврки типизированных объектов.

# @pytest.mark.parametrize(
# ["obj", "obj_t"],
# [
# ([1, 2], List[int]),
# ({"field": 1}, Dict[str, int]),
# ({1, 2}, Set[int]),
# ],
# )
# def test_with_non_empty_collections_and_typed_generics(obj, obj_t):
# assert impr_isinstance(obj, obj_t)


# @pytest.mark.parametrize(
# ["obj", "obj_t"],
# [
# ([1, None], List[int]),
# ({"field": None}, Dict[str, int]),
# ({1, None}, Set[int]),
# ],
# )
# def test_with_incorect_non_empty_collections_and_typed_generics(obj, obj_t):
# assert not impr_isinstance(obj, obj_t)
