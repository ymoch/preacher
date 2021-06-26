"""
Retrying utilities.
"""

import time

from typing import Callable, TypeVar


T = TypeVar("T")


def retry_while_false(
    func: Callable[[], T],
    attempts: int = 1,
    delay: float = 0.1,
    predicate: Callable[[T], bool] = bool,
) -> T:
    if attempts < 1:
        raise ValueError(f"`attempts` must be positive, given {attempts}")

    for _ in range(attempts - 1):
        result = func()
        if predicate(result):
            return result
        time.sleep(delay)

    return func()
