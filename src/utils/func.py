from typing import Tuple, get_args, get_origin, Any, Type
from src.step import Step


def get_step_types(cls: Type[Step]) -> Tuple[Type[Any], Type[Any]]:
    for base_cls in cls.__orig_bases__:
        if get_origin(base_cls) is Step:
            input_type, output_type = get_args(base_cls)
            return input_type, output_type
    raise ValueError("Класс не являться неслдеником Step")
