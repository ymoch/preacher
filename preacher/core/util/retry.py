"""
Retrying utilities.
"""

import time

from typing import Callable, TypeVar


T = TypeVar('T')


def retry_while_false(func: Callable, attempts: int = 1, delay: float = 0.1):
    if attempts < 1:
        raise ValueError(f'`attempts` must be positive, given {attempts}')

    for _ in range(attempts - 1):
        result = func()
        if result:
            return result
        time.sleep(delay)

    return func()
