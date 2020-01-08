from typing import Union

ScalarType = Union[bool, int, float, str]

_SCALAR_TYPES = [bool, int, float, str]


def is_scalar(value: object) -> bool:
    return any(isinstance(value, t) for t in _SCALAR_TYPES)
