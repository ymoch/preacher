"""Request compilation."""

from preacher.core.request import Request


def compile(obj: dict) -> Request:
    """
    >>> request = compile({})
    """
    path = obj.get('path', '')
    query = obj.get('query', {})
    return Request(path=path, query=query)
