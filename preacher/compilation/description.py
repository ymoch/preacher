"""Description compilation."""

from collections.abc import Mapping

from preacher.core.description import Description
from .error import CompilationError
from .predicate import compile as compile_predicate
from .extraction import compile as compile_extraction
from .util import run_on_key, map_on_key


_KEY_DESCRIBE = 'describe'
_KEY_IT_SHOULD = 'it_should'


def compile(obj: Mapping) -> Description:
    """
    >>> from unittest.mock import call, patch, sentinel
    >>> extraction_patch = patch(
    ...     f'{__name__}.compile_extraction',
    ...     return_value=sentinel.extraction,
    ... )
    >>> predicate_patch = patch(
    ...     f'{__name__}.compile_predicate',
    ...     return_value=sentinel.predicate,
    ... )

    >>> compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Description.describe ...

    >>> with extraction_patch as extraction_mock, \\
    ...      predicate_patch as predicate_mock:
    ...     description = compile({
    ...         'describe': 'foo',
    ...         'it_should': 'string',
    ...     })
    ...     extraction_mock.assert_called_with('foo')
    ...     predicate_mock.assert_called_once_with('string')
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate]

    >>> with extraction_patch as extraction_mock, \\
    ...      predicate_patch as predicate_mock:
    ...     description = compile({
    ...         'describe': 'foo',
    ...         'it_should': {'key': 'value'}
    ...     })
    ...     extraction_mock.assert_called_once_with('foo')
    ...     predicate_mock.assert_called_once_with({'key': 'value'})
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate]

    >>> with extraction_patch as extraction_mock, \\
    ...      predicate_patch as predicate_mock:
    ...     description = compile({
    ...         'describe': {'key': 'value'},
    ...         'it_should': [{'key1': 'value1'}, {'key2': 'value2'}]
    ...     })
    ...     extraction_mock.assert_called_once_with({'key': 'value'})
    ...     predicate_mock.assert_has_calls([
    ...         call({'key1': 'value1'}),
    ...         call({'key2': 'value2'}),
    ...     ])
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate, sentinel.predicate]
    """
    extraction_obj = obj.get(_KEY_DESCRIBE)
    if (
        not isinstance(extraction_obj, Mapping)
        and not isinstance(extraction_obj, str)
    ):
        raise CompilationError(
            message='Description.describe must be a mapping',
            path=[_KEY_DESCRIBE],
        )
    extraction = run_on_key(_KEY_DESCRIBE, compile_extraction, extraction_obj)

    predicate_objs = obj.get(_KEY_IT_SHOULD, [])
    if not isinstance(predicate_objs, list):
        predicate_objs = [predicate_objs]
    predicates = list(
        map_on_key(_KEY_IT_SHOULD, compile_predicate, predicate_objs)
    )

    return Description(extraction=extraction, predicates=predicates)
