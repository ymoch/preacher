"""Response description compilations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Optional, List

from preacher.core.description import Description, Predicate
from preacher.core.response import ResponseDescription
from .body import BodyDescriptionCompiler, Compiled as BodyCompiled
from .description import DescriptionCompiler
from .error import CompilationError, on_key
from .predicate import PredicateCompiler
from .util import map_compile

_KEY_STATUS_CODE = 'status_code'
_KEY_HEADERS = 'headers'
_KEY_BODY = 'body'


@dataclass(frozen=True)
class Compiled:
    status_code: Optional[List[Predicate]] = None
    headers: Optional[List[Description]] = None
    body: Optional[BodyCompiled] = None

    def convert(self) -> ResponseDescription:
        return ResponseDescription(
            status_code=self.status_code,
            headers=self.headers,
            body=self.body.convert() if self.body else None,
        )


class ResponseDescriptionCompiler:

    def __init__(
        self,
        predicate: PredicateCompiler,
        description: DescriptionCompiler,
        body: BodyDescriptionCompiler,
        default_status_code: Optional[List[Predicate]] = None,
        default_headers: Optional[List[Description]] = None,
    ):
        self._predicate = predicate
        self._description = description
        self._body = body
        self._default_status_code = default_status_code or []
        self._default_headers = default_headers or []

    def of_default(self, obj: object) -> ResponseDescriptionCompiler:
        compiled = self._compile(obj)
        return ResponseDescriptionCompiler(
            predicate=self._predicate,
            description=self._description,
            body=self._body.of_default(compiled.body),
            default_status_code=compiled.status_code,
            default_headers=compiled.headers,
        )

    def compile(self, obj: object) -> ResponseDescription:
        """`obj` should be a mapping."""
        return self._compile(obj).convert()

    def _compile(self, obj: object) -> Compiled:
        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        status_code = self._default_status_code
        if _KEY_STATUS_CODE in obj:
            status_code_obj = obj.get(_KEY_STATUS_CODE)
            with on_key(_KEY_STATUS_CODE):
                status_code = self._compile_status_code(status_code_obj)

        headers = self._default_headers
        if _KEY_HEADERS in obj:
            headers_obj = obj.get(_KEY_HEADERS)
            with on_key(_KEY_HEADERS):
                headers = self._compile_headers(headers_obj)

        body_obj = obj.get(_KEY_BODY, {})
        body = self._body.compile(body_obj)

        return Compiled(status_code=status_code, headers=headers, body=body)

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
