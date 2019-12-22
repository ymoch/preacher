"""
Functional utilities.
"""

from typing import TypeVar

T = TypeVar('T')


def identify(value: T, *_args, **_kwargs) -> T:
    """
    Returns the first argument.
    >>> identify(None)
    >>> identify(1)
    1
    >>> identify('a')
    'a'
    >>> identify([1, 2, 3])
    [1, 2, 3]

    Ignores extra arguments.
    >>> identify(1, 2, key='value')
    1
    """
    return value
