from datetime import datetime

from preacher.core.scenario import ParameterValue
from .error import CompilationError


def ensure_scalar(
    value: object,
    error_message: str = 'Must be a scalar',
) -> ParameterValue:
    if value is None:
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    raise CompilationError(error_message)
