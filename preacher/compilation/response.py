"""Response description compilations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional, List

from preacher.core.description import Description, Predicate
from preacher.core.response import ResponseDescription
from .body import BodyDescriptionCompiler
from .description import DescriptionCompiler
from .error import CompilationError, on_key
from .predicate import PredicateCompiler
from .util import map_compile

_KEY_STATUS_CODE = 'status_code'
_KEY_HEADERS = 'headers'
_KEY_BODY = 'body'


class ResponseDescriptionCompiler:

    def __init__(
        self,
        predicate: PredicateCompiler,
        description: DescriptionCompiler,
        body: BodyDescriptionCompiler,
        default: Optional[ResponseDescription] = None,
    ):
        self._predicate = predicate
        self._description = description
        self._body = body
        self._default = default or ResponseDescription()

    def of_default(
        self,
        default: ResponseDescription,
    ) -> ResponseDescriptionCompiler:
        body = self._body
        if default.body:
            body = body.of_default(default.body)

        return ResponseDescriptionCompiler(
            predicate=self._predicate,
            description=self._description,
            body=body,
            default=default,
        )

    def compile(self, obj: object) -> ResponseDescription:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        status_code = self._default.status_code
        status_code_obj = obj.get(_KEY_STATUS_CODE)
        if status_code_obj is not None:
            with on_key(_KEY_STATUS_CODE):
                status_code = self._compile_status_code(status_code_obj)

        headers = self._default.headers
        headers_obj = obj.get(_KEY_HEADERS)
        if headers_obj is not None:
            with on_key(_KEY_HEADERS):
                headers = self._compile_headers(headers_obj)

        body = self._default.body
        body_obj = obj.get(_KEY_BODY)
        if body_obj is not None:
            body = self._body.compile(body_obj)

        return ResponseDescription(
            status_code=status_code,
            headers=headers,
            body=body,
        )

    def _compile_status_code(self, obj: object) -> List[Predicate]:
        if not isinstance(obj, list):
            obj = [obj]
        return list(map_compile(self._predicate.compile, obj))

    def _compile_headers(self, obj: object) -> List[Description]:
        if isinstance(obj, Mapping):
            obj = [obj]
        if not isinstance(obj, list):
            message = f'Must be a list or a mapping, given {type(obj)}'
            raise CompilationError(message)

        return list(map_compile(self._description.compile, obj))
