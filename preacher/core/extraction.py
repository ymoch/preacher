"""Extraction."""

from .description import Extraction

from pyjq import compile as jq_compile


def with_jq(query: str) -> Extraction:
    """
    Returns a extractor of given `jq`.

    >>> extract = with_jq('.foo')
    >>> extract({'not_foo': 'bar'})
    >>> extract({'foo': 'bar'})
    'bar'
    >>> extract({'foo': ['bar', 'baz', 1, 2]})
    ['bar', 'baz', 1, 2]
    """
    return jq_compile(query).first
