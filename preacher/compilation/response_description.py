"""Response description compilations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Optional, List

from preacher.core.description import Description, Predicate
from preacher.core.response_description import ResponseDescription
from .body_description import BodyDescriptionCompiler, BodyDescriptionCompiled
from .description import DescriptionCompiler
from .error import CompilationError
from .predicate import PredicateCompiler
from .util import map_on_key, or_default, run_on_key


_KEY_STATUS_CODE = 'status_code'
_KEY_HEADERS = 'headers'
_KEY_BODY = 'body'


@dataclass(frozen=True)
class Compiled:
    status_code: Optional[List[Predicate]] = None
    headers: Optional[List[Description]] = None
    body: Optional[BodyDescriptionCompiled] = None

    def updated(self, updater: Compiled) -> Compiled:
        return Compiled(
            status_code=or_default(updater.status_code, self.status_code),
            headers=or_default(updater.headers, self.headers),
            body=or_default(updater.body, self.body),
        )

    def to_response_description(self) -> ResponseDescription:
        return ResponseDescription(
            status_code_predicates=or_default(self.status_code, []),
            headers_descriptions=or_default(self.headers, []),
            body_description=self.body.convert() if self.body else None,
        )


class ResponseDescriptionCompiler:

    def __init__(
        self,
        default: Optional[Compiled] = None,
        predicate_compiler: Optional[PredicateCompiler] = None,
        description_compiler: Optional[DescriptionCompiler] = None,
        body_description_compiler: Optional[BodyDescriptionCompiler] = None,
    ):
        self._default = default or Compiled()
        self._predicate_compiler = predicate_compiler or PredicateCompiler()
        self._description_compiler = (
            description_compiler
            or DescriptionCompiler(predicate_compiler=self._predicate_compiler)
        )
        self._body_description_compiler = (
            body_description_compiler
            or BodyDescriptionCompiler(
                description_compiler=self._description_compiler
            )
        )

    def compile(self, obj: Any) -> ResponseDescription:
        compiled = self._compile(obj)
        return self._default.updated(compiled).to_response_description()

    def _compile(self, obj: Any):
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        status_code = None
        status_code_obj = obj.get(_KEY_STATUS_CODE)
        if status_code_obj is not None:
            status_code = self._compile_status_code(status_code_obj)

        headers = None
        headers_obj = obj.get(_KEY_HEADERS)
        if headers_obj is not None:
            headers = self._compile_headers(headers_obj)

        body = None
        body_obj = obj.get(_KEY_BODY)
        if body_obj is not None:
            body = run_on_key(
                _KEY_BODY,
                self._body_description_compiler.compile,
                body_obj,
            )

        return Compiled(status_code=status_code, headers=headers, body=body)

    def _compile_status_code(self, obj: Any) -> List[Predicate]:
        if not isinstance(obj, list):
            obj = [obj]
        return list(map_on_key(
            _KEY_STATUS_CODE,
            self._predicate_compiler.compile,
            obj,
        ))

    def _compile_headers(self, obj: Any) -> List[Description]:
        if isinstance(obj, Mapping):
            obj = [obj]
        if not isinstance(obj, list):
            message = 'Must be a list or a mapping'
            raise CompilationError(message=message, path=[_KEY_HEADERS])
        return list(map_on_key(
            _KEY_HEADERS,
            self._description_compiler.compile,
            obj,
        ))
