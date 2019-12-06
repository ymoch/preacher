from typing import TypeVar


T = TypeVar('T')


def identify(arg: T) -> T:
    """
    >>> identify(None)
    >>> identify(1)
    1
    >>> identify('str')
    'str'
    """
    return arg
