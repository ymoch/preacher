from typing import TypeVar


T = TypeVar('T')


def identify(value: T, **kwargs) -> T:
    """
    >>> identify(None)
    >>> identify(1)
    1
    >>> identify('A', key='value')
    'A'
    """
    return value
