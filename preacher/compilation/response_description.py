"""Response description compilations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional

from preacher.core.description import Description
from preacher.core.response_description import ResponseDescription
from .error import CompilationError
from .description import DescriptionCompiler
from .predicate import PredicateCompiler
from .util import map_on_key


_KEY_STATUS_CODE = 'status_code'
_KEY_BODY = 'body'


class ResponseDescriptionCompiler:
    """
    >>> from unittest.mock import MagicMock, call, patch, sentinel
    >>> def default_predicate_compiler() -> PredicateCompiler:
    ...     return MagicMock(
    ...         spec=PredicateCompiler,
    ...         compile=MagicMock(return_value=sentinel.predicate),
    ...     )
    >>> def default_description_compiler() -> DescriptionCompiler:
    ...     return MagicMock(
    ...         spec=DescriptionCompiler,
    ...         compile=MagicMock(return_value=sentinel.description),
    ... )

    >>> predicate_compiler = default_predicate_compiler()
    >>> description_compiler = default_description_compiler()
    >>> compiler = ResponseDescriptionCompiler(
    ...     predicate_compiler=predicate_compiler,
    ...     description_compiler=description_compiler,
    ... )
    >>> response_description = compiler.compile({})
    >>> response_description.status_code_predicates
    []
    >>> response_description.body_descriptions
    []
    >>> predicate_compiler.compile.assert_not_called()
    >>> description_compiler.compile.assert_not_called()

    >>> compiler = ResponseDescriptionCompiler()
    >>> compiler.compile({'body': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: body

    >>> compiler = ResponseDescriptionCompiler()
    >>> compiler.compile({'body': ['str']})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Description ...: body[0]

    >>> predicate_compiler = default_predicate_compiler()
    >>> description_compiler = default_description_compiler()
    >>> compiler = ResponseDescriptionCompiler(
    ...     predicate_compiler=predicate_compiler,
    ...     description_compiler=description_compiler,
    ... )
    >>> response_description = compiler.compile({
    ...     'status_code': 402,
    ...     'body': {'key1': 'value1'}}
    ... )
    >>> response_description.status_code_predicates
    [sentinel.predicate]
    >>> response_description.body_descriptions
    [sentinel.description]
    >>> predicate_compiler.compile.assert_called_once_with(402)
    >>> description_compiler.compile.assert_called_once_with(
    ...     {'key1': 'value1'}
    ... )

    >>> predicate_compiler = default_predicate_compiler()
    >>> description_compiler = default_description_compiler()
    >>> compiler = ResponseDescriptionCompiler(
    ...     predicate_compiler=predicate_compiler,
    ...     description_compiler=description_compiler,
    ... )
    >>> response_description = compiler.compile({
    ...     'status_code': [{'be_greater_than': 0}, {'be_less_than': 400}],
    ...     'body': [{'key1': 'value1'}, {'key2': 'value2'}],
    ... })
    >>> response_description.status_code_predicates
    [sentinel.predicate, sentinel.predicate]
    >>> response_description.body_descriptions
    [sentinel.description, sentinel.description]
    >>> predicate_compiler.compile.assert_has_calls([
    ...     call({'be_greater_than': 0}),
    ...     call({'be_less_than': 400}),
    ... ])
    >>> description_compiler.compile.assert_has_calls([
    ...     call({'key1': 'value1'}),
    ...     call({'key2': 'value2'}),
    ... ])
    """
    def __init__(
        self: ResponseDescriptionCompiler,
        predicate_compiler: Optional[PredicateCompiler] = None,
        description_compiler: Optional[DescriptionCompiler] = None,
    ) -> None:
        self._predicate_compiler = predicate_compiler or PredicateCompiler()
        self._description_compiler = (
            description_compiler
            or DescriptionCompiler(
                predicate_compiler=self._predicate_compiler
            )
        )

    def compile(
        self: ResponseDescriptionCompiler,
        obj: Mapping,
    ) -> ResponseDescription:
        status_code_predicate_objs = obj.get(_KEY_STATUS_CODE, [])
        if not isinstance(status_code_predicate_objs, list):
            status_code_predicate_objs = [status_code_predicate_objs]
        status_code_predicates = list(map_on_key(
            key=_KEY_STATUS_CODE,
            func=self._predicate_compiler.compile,
            items=status_code_predicate_objs,
        ))

        body_description_objs = obj.get(_KEY_BODY, [])
        if isinstance(body_description_objs, Mapping):
            body_description_objs = [body_description_objs]
        if not isinstance(body_description_objs, list):
            raise CompilationError(
                message='ResponseDescription.body must be a list or a mapping',
                path=[_KEY_BODY],
            )
        body_descriptions = list(map_on_key(
            key=_KEY_BODY,
            func=self._compile_description,
            items=body_description_objs,
        ))

        return ResponseDescription(
            status_code_predicates=status_code_predicates,
            body_descriptions=body_descriptions,
        )

    def _compile_description(
        self: ResponseDescriptionCompiler,
        obj: Any,
    ) -> Description:
        if not isinstance(obj, Mapping):
            raise CompilationError('Description must be a mapping')
        return self._description_compiler.compile(obj)
