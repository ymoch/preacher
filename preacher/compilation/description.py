"""Description compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

from preacher.core.description import Description
from .error import CompilationError
from .predicate import PredicateCompiler
from .extraction import ExtractionCompiler
from .util import run_on_key, map_on_key


_KEY_DESCRIBE = 'describe'
_KEY_SHOULD = 'should'


class DescriptionCompiler:
    """
    >>> from unittest.mock import MagicMock, call, sentinel
    >>> def default_extraction_compiler() -> ExtractionCompiler:
    ...     return MagicMock(
    ...         spec=ExtractionCompiler,
    ...         compile=MagicMock(return_value=sentinel.extraction),
    ...     )
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

    >>> extraction_compiler = default_extraction_compiler()
    >>> predicate_compiler = default_predicate_compiler()
    >>> compiler = DescriptionCompiler(
    ...     extraction_compiler=extraction_compiler,
    ...     predicate_compiler=predicate_compiler,
    ... )
    >>> description = compiler.compile({
    ...     'describe': 'foo',
    ...     'should': 'string',
    ... })
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate]
    >>> extraction_compiler.compile.assert_called_with('foo')
    >>> predicate_compiler.compile.assert_called_once_with('string')

    >>> extraction_compiler = default_extraction_compiler()
    >>> predicate_compiler = default_predicate_compiler()
    >>> compiler = DescriptionCompiler(
    ...     extraction_compiler=extraction_compiler,
    ...     predicate_compiler=predicate_compiler,
    ... )
    >>> description = compiler.compile({
    ...     'describe': 'foo',
    ...     'should': {'key': 'value'}
    ... })
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate]
    >>> extraction_compiler.compile.assert_called_once_with('foo')
    >>> predicate_compiler.compile.assert_called_once_with({'key': 'value'})

    >>> extraction_compiler = default_extraction_compiler()
    >>> predicate_compiler = default_predicate_compiler()
    >>> compiler = DescriptionCompiler(
    ...     extraction_compiler=extraction_compiler,
    ...     predicate_compiler=predicate_compiler,
    ... )
    >>> description = compiler.compile({
    ...     'describe': {'key': 'value'},
    ...     'should': [{'key1': 'value1'}, {'key2': 'value2'}]
    ... })
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate, sentinel.predicate]
    >>> extraction_compiler.compile.assert_called_once_with({'key': 'value'})
    >>> predicate_compiler.compile.assert_has_calls([
    ...     call({'key1': 'value1'}),
    ...     call({'key2': 'value2'}),
    ... ])
    """
    def __init__(
        self: DescriptionCompiler,
        extraction_compiler: Optional[ExtractionCompiler] = None,
        predicate_compiler: Optional[PredicateCompiler] = None,
    ) -> None:
        self._extraction_compiler = extraction_compiler or ExtractionCompiler()
        self._predicate_compiler = predicate_compiler or PredicateCompiler()

    def compile(self: DescriptionCompiler, obj: Mapping):
        extraction_obj = obj.get(_KEY_DESCRIBE)
        if (
            not isinstance(extraction_obj, Mapping)
            and not isinstance(extraction_obj, str)
        ):
            raise CompilationError(
                message='Description.describe must be a mapping or a string',
                path=[_KEY_DESCRIBE],
            )
        extraction = run_on_key(
            _KEY_DESCRIBE,
            self._extraction_compiler.compile,
            extraction_obj
        )

        predicate_objs = obj.get(_KEY_SHOULD, [])
        if not isinstance(predicate_objs, list):
            predicate_objs = [predicate_objs]
        predicates = list(map_on_key(
            _KEY_SHOULD,
            self._predicate_compiler.compile,
            predicate_objs,
        ))

        return Description(extraction=extraction, predicates=predicates)
