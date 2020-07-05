"""
Timedelta compilation.
"""

import re
from datetime import timedelta

from .error import CompilationError
from .util import compile_str

TIMEDELTA_PATTERN = re.compile(r'([+\-]?\d+)\s*(day|hour|minute|second)s?')


def compile_timedelta(obj: object) -> timedelta:
    """
    Args:
        obj: The interpreted value, which should be a string.

    Raises:
        InterpretationError: When interpretation fails.
    """
    obj = compile_str(obj)
    normalized = obj.strip().lower()
    if normalized == 'now':
        return timedelta()

    match = TIMEDELTA_PATTERN.match(normalized)
    if not match:
        raise CompilationError(f'Invalid timedelta format: {obj}')
    offset = int(match.group(1))
    unit = match.group(2) + 's'
    return timedelta(**{unit: offset})
