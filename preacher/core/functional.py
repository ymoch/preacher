"""
Functional utilities.
"""

from typing import TypeVar

T = TypeVar('T')


def identify(value: T, *_args, **_kwargs) -> T:
    """Returns the first argument, ignoring extra arguments."""
    return value
