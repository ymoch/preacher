"""Matcher compilation."""

import hamcrest
from hamcrest.core.matcher import Matcher

from preacher.compilation.error import CompilationError


_STATIC_MATCHER_MAP = {
    # For objects.
    'is_null': hamcrest.is_(hamcrest.none()),
    'is_not_null': hamcrest.is_(hamcrest.not_none()),
    # For collections.
    'is_empty': hamcrest.is_(hamcrest.empty()),
}


def _compile_static_matcher(name: str) -> Matcher:
    """
    >>> _compile_static_matcher('invalid_name')
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... 'invalid_name'

    >>> matcher = _compile_static_matcher('is_null')
    >>> assert matcher.matches(None)
    >>> assert not matcher.matches(False)

    >>> matcher = _compile_static_matcher('is_not_null')
    >>> assert not matcher.matches(None)
    >>> assert matcher.matches('False')

    >>> matcher = _compile_static_matcher('is_empty')
    >>> assert not matcher.matches(None)
    >>> assert not matcher.matches(0)
    >>> assert matcher.matches('')
    >>> assert not matcher.matches('A')
    >>> assert matcher.matches([])
    >>> assert not matcher.matches([1])
    """
    matcher = _STATIC_MATCHER_MAP.get(name)
    if not matcher:
        raise CompilationError(f'Invalid matcher: \'{name}\'')
    return matcher
