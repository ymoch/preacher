"""Compilation."""

from typing import Any, Callable, Mapping, Union

import hamcrest
from hamcrest.core.matcher import Matcher

from . import extraction
from . import predicate
from .description import Predicate, Extraction


_EXTRACTION_MAP: Mapping[str, Callable[[str], Extraction]] = {
    'jq': extraction.with_jq,
}
_EXTRACTION_KEYS = frozenset(_EXTRACTION_MAP.keys())
_STATIC_MATCHER_MAP: Mapping[str, Matcher] = {
    # For objects.
    'is_null': hamcrest.is_(hamcrest.none()),
    'is_not_null': hamcrest.is_(hamcrest.not_none()),
    # For collections.
    'is_empty': hamcrest.is_(hamcrest.empty()),
}
_VALUE_MATCHER_FUNCTION_MAP: Mapping[str, Callable[[Any], Matcher]] = {
    # For objects.
    'equals_to': lambda expected: hamcrest.is_(hamcrest.equal_to(expected)),
    'has_length': lambda expected: hamcrest.has_length(expected),
    # For numbers.
    'is_greater_than': (
        lambda value: hamcrest.is_(hamcrest.greater_than(value))
    ),
    'is_greater_than_or_equal_to': (
        lambda value: hamcrest.is_(hamcrest.greater_than_or_equal_to(value))
    ),
    'is_less_than': (
        lambda value: hamcrest.is_(hamcrest.less_than(value))
    ),
    'is_less_than_or_equal_to': (
        lambda value: hamcrest.is_(hamcrest.less_than_or_equal_to(value))
    ),
    # For strings.
    'contains_string': lambda value: hamcrest.contains_string(value),
    'starts_with': lambda value: hamcrest.starts_with(value),
    'ends_with': lambda value: hamcrest.ends_with(value),
    'matches_regexp': lambda value: hamcrest.matches_regexp(value),
}
_PREDICATE_KEYS = frozenset(_VALUE_MATCHER_FUNCTION_MAP.keys())


class CompilationError(Exception):
    """Compilation errors."""
    pass


def compile_extraction(description_object: dict) -> Extraction:
    """
    >>> compile_extraction({})
    Traceback (most recent call last):
        ...
    preacher.core.compilation.CompilationError: ... has 0

    >>> compile_extraction({'jq': '.foo'})({'foo': 'bar'})
    'bar'
    """
    keys = _EXTRACTION_KEYS.intersection(description_object.keys())
    if len(keys) != 1:
        raise CompilationError(
            'Description object must have only 1 valid extraction key'
            f', but has {len(keys)}'
        )
    key = next(iter(keys))

    return _EXTRACTION_MAP[key](description_object[key])


def compile_predicate(predicate_object: Union[str, dict]) -> Predicate:
    """
    >>> compile_predicate('invalid_key')
    Traceback (most recent call last):
        ...
    preacher.core.compilation.CompilationError: ... 'invalid_key'

    >>> predicate = compile_predicate('is_null')
    >>> predicate(None).is_valid
    True
    >>> predicate(True).is_valid
    False

    >>> predicate = compile_predicate('is_not_null')
    >>> predicate(None).is_valid
    False
    >>> predicate(False).is_valid
    True

    >>> predicate = compile_predicate('is_empty')
    >>> predicate(None).is_valid
    False
    >>> predicate(0).is_valid
    False
    >>> predicate('').is_valid
    True
    >>> predicate([]).is_valid
    True
    >>> predicate('A').is_valid
    False
    >>> predicate([1]).is_valid
    False

    >>> compile_predicate({})
    Traceback (most recent call last):
        ...
    preacher.core.compilation.CompilationError: ... has 0

    >>> compile_predicate({'equals_to': 0, 'not': {'equal_to': 1}})
    Traceback (most recent call last):
        ...
    preacher.core.compilation.CompilationError: ... has 2

    >>> predicate = compile_predicate({'has_length': 1})
    >>> predicate(None).is_valid
    False
    >>> predicate('').is_valid
    False
    >>> predicate([]).is_valid
    False
    >>> predicate('A').is_valid
    True
    >>> predicate([1]).is_valid
    True

    >>> compile_predicate({'invalid_key': 0})
    Traceback (most recent call last):
        ...
    preacher.core.compilation.CompilationError: ... 'invalid_key'

    >>> predicate = compile_predicate({'equals_to': 1})
    >>> predicate(0).is_valid
    False
    >>> predicate('1').is_valid
    False
    >>> predicate(1).is_valid
    True

    >>> predicate = compile_predicate({'is_greater_than': 0})
    >>> predicate(-1).is_valid
    False
    >>> predicate(0).is_valid
    False
    >>> predicate(1).is_valid
    True

    >>> predicate = compile_predicate({'is_greater_than_or_equal_to': 0})
    >>> predicate(-1).is_valid
    False
    >>> predicate(0).is_valid
    True
    >>> predicate(1).is_valid
    True

    >>> predicate = compile_predicate({'is_less_than': 0})
    >>> predicate(-1).is_valid
    True
    >>> predicate(0).is_valid
    False
    >>> predicate(1).is_valid
    False

    >>> predicate = compile_predicate({'is_less_than_or_equal_to': 0})
    >>> predicate(-1).is_valid
    True
    >>> predicate(0).is_valid
    True
    >>> predicate(1).is_valid
    False

    >>> predicate = compile_predicate({'contains_string': '0'})
    >>> predicate(0).is_valid
    False
    >>> predicate('012').is_valid
    True
    >>> predicate('123').is_valid
    False

    >>> predicate = compile_predicate({'starts_with': 'AB'})
    >>> predicate(0).is_valid
    False
    >>> predicate('ABC').is_valid
    True
    >>> predicate('ACB').is_valid
    False

    >>> predicate = compile_predicate({'ends_with': 'BC'})
    >>> predicate(0).is_valid
    False
    >>> predicate('ABC').is_valid
    True
    >>> predicate('ACB').is_valid
    False

    >>> predicate = compile_predicate({'matches_regexp': '^A*B$'})
    >>> predicate('B').is_valid
    True
    >>> predicate('ACB').is_valid
    False

    TODO: Should return `False` when the value type is not `str`.
    >>> predicate(0).is_valid
    Traceback (most recent call last):
        ...
    TypeError: ...
    """
    if isinstance(predicate_object, str):
        matcher = _STATIC_MATCHER_MAP.get(predicate_object)
        if not matcher:
            raise CompilationError(
                f'Invalid predicate: \'{predicate_object}\''
            )
        return predicate.of_hamcrest_matcher(matcher)

    if len(predicate_object) != 1:
        raise CompilationError(
            'Predicate must have only 1 element'
            f', but has {len(predicate_object)}'
        )
    key, value = next(iter(predicate_object.items()))
    if key in _VALUE_MATCHER_FUNCTION_MAP:
        matcher = _VALUE_MATCHER_FUNCTION_MAP[key](value)
        return predicate.of_hamcrest_matcher(matcher)

    raise CompilationError(f'Unrecognized predicate key: \'{key}\'')
