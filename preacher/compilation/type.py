from preacher.core.scenario import ScalarType
from .error import CompilationError


def ensure_scalar(
    value: object,
    error_message: str = 'Must be a scalar',
) -> ScalarType:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, str):
        return value
    raise CompilationError(error_message)
