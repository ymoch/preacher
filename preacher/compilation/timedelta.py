"""
Timedelta compilation.
"""

import re
from datetime import timedelta

from .error import CompilationError

TIMEDELTA_PATTERN = re.compile(r'([+\-]?\d+)\s*(day|hour|minute|second)s?')


def compile_timedelta(value: object) -> timedelta:
    """
    Args:
        value: The interpreted value, which should be a string.

    Raises:
        InterpretationError: When interpretation fails.
    """
    if not isinstance(value, str):
        raise CompilationError(f'Must be a string, given {type(value)}')

    normalized = value.strip().lower()

    if normalized == 'now':
        return timedelta()

    match = TIMEDELTA_PATTERN.match(normalized)
    if not match:
        raise CompilationError(f'Invalid timedelta format: {value}')
    offset = int(match.group(1))
    unit = match.group(2) + 's'
    return timedelta(**{unit: offset})
