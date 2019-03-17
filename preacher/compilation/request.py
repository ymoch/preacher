"""Request compilation."""

from preacher.core.request import Request


def compile(obj: dict) -> Request:
    """
    >>> request = compile({})
    """
    path = obj.get('path', '')
    params = obj.get('params', {})
    return Request(path=path, params=params)
