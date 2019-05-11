"""Description compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

from preacher.core.description import Description
from .error import CompilationError
from .predicate import PredicateCompiler
from .extraction import compile as compile_extraction
from .util import run_on_key, map_on_key


_KEY_DESCRIBE = 'describe'
_KEY_IT_SHOULD = 'it_should'


class DescriptionCompiler:
    """
    >>> from unittest.mock import MagicMock, call, patch, sentinel
    >>> extraction_patch = patch(
    ...     f'{__name__}.compile_extraction',
    ...     return_value=sentinel.extraction,
    ... )
    >>> def default_predicate_compiler() -> PredicateCompiler:
    ...     return MagicMock(
    ...         spec=PredicateCompiler,
    ...         compile=MagicMock(return_value=sentinel.predicate),
    ...     )

    >>> compiler = DescriptionCompiler()
    >>> compiler.compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Description.describe ...

    >>> predicate_compiler = default_predicate_compiler()
    >>> compiler = DescriptionCompiler(predicate_compiler)
    >>> with extraction_patch as extraction_mock:
    ...     description = compiler.compile({
    ...         'describe': 'foo',
    ...         'it_should': 'string',
    ...     })
    ...     extraction_mock.assert_called_with('foo')
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate]
    >>> predicate_compiler.compile.assert_called_once_with('string')

    >>> predicate_compiler = default_predicate_compiler()
    >>> compiler = DescriptionCompiler(predicate_compiler)
    >>> with extraction_patch as extraction_mock:
    ...     description = compiler.compile({
    ...         'describe': 'foo',
    ...         'it_should': {'key': 'value'}
    ...     })
    ...     extraction_mock.assert_called_once_with('foo')
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate]
    >>> predicate_compiler.compile.assert_called_once_with({'key': 'value'})

    >>> predicate_compiler = default_predicate_compiler()
    >>> compiler = DescriptionCompiler(predicate_compiler)
    >>> with extraction_patch as extraction_mock:
    ...     description = compiler.compile({
    ...         'describe': {'key': 'value'},
    ...         'it_should': [{'key1': 'value1'}, {'key2': 'value2'}]
    ...     })
    ...     extraction_mock.assert_called_once_with({'key': 'value'})
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate, sentinel.predicate]
    >>> predicate_compiler.compile.assert_has_calls([
    ...     call({'key1': 'value1'}),
    ...     call({'key2': 'value2'}),
    ... ])
    """
    def __init__(
        self: DescriptionCompiler,
        predicate_compiler: Optional[PredicateCompiler] = None,
    ) -> None:
        self._predicate_compiler = predicate_compiler or PredicateCompiler()

    def compile(self: DescriptionCompiler, obj: Mapping):
        extraction_obj = obj.get(_KEY_DESCRIBE)
        if (
            not isinstance(extraction_obj, Mapping)
            and not isinstance(extraction_obj, str)
        ):
            raise CompilationError(
                message='Description.describe must be a mapping',
                path=[_KEY_DESCRIBE],
            )
        extraction = run_on_key(
            _KEY_DESCRIBE,
            compile_extraction,
            extraction_obj
        )

        predicate_objs = obj.get(_KEY_IT_SHOULD, [])
        if not isinstance(predicate_objs, list):
            predicate_objs = [predicate_objs]
        predicates = list(map_on_key(
            _KEY_IT_SHOULD,
            self._predicate_compiler.compile,
            predicate_objs,
        ))

        return Description(extraction=extraction, predicates=predicates)
