from typing import Callable


def retry_case(func: Callable, attempts: int = 1):
    if attempts < 1:
        raise ValueError(f'`attempts` must be positive, given {attempts}')

    for _ in range(attempts):
        result = func()
        if result.status.is_succeeded:
            return result

    return result
