from typing import Callable, TypeVar


T = TypeVar('T')


def retry_while_false(func: Callable, attempts: int = 1):
    if attempts < 1:
        raise ValueError(f'`attempts` must be positive, given {attempts}')

    for _ in range(attempts):
        result = func()
        if result:
            return result

    return result
