"""Datetime compilations."""

import re
from datetime import timedelta

from .error import CompilationError


RELATIVE_DATETIME_PATTERN = re.compile(
    r'([+\-]?\d+)\s*(day|hour|minute|second)s?'
)


def compile_timedelta(value: str) -> timedelta:
    match = RELATIVE_DATETIME_PATTERN.search(value.lower())
    if not match:
        raise CompilationError(f'Invalid datetime format: {value}')
    offset = int(match.group(1))
    unit = match.group(2) + 's'
    return timedelta(**{unit: offset})
