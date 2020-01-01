"""Response description compilations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Optional, List, Any, Dict

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

    def of_default(self, default: Compiled) -> ResponseDescriptionCompiler:
        return ResponseDescriptionCompiler(
            default=default,
            predicate_compiler=self._predicate_compiler,
            description_compiler=self._description_compiler,
            body_description_compiler=(
                self._body_description_compiler.of_default(default.body)
            ),
        )

    def compile(self, obj: object) -> Compiled:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        replacements: Dict[str, Any] = {}

        status_code_obj = obj.get(_KEY_STATUS_CODE)
        if status_code_obj is not None:
            replacements['status_code'] = (
                self._compile_status_code(status_code_obj)
            )

        headers_obj = obj.get(_KEY_HEADERS)
        if headers_obj is not None:
            with on_key(_KEY_HEADERS):
                replacements['headers'] = self._compile_headers(headers_obj)

        body_obj = obj.get(_KEY_BODY)
        if body_obj is not None:
            with on_key(_KEY_BODY):
                replacements['body'] = self._body_description_compiler.compile(
                    body_obj,
                )

        return replace(self._default, **replacements)

    def _compile_status_code(self, obj: object) -> List[Predicate]:
        if not isinstance(obj, list):
            obj = [obj]
        with on_key(_KEY_STATUS_CODE):
            return list(map_compile(
                self._predicate_compiler.compile,
                obj,
            ))

    def _compile_headers(self, obj: object) -> List[Description]:
        if isinstance(obj, Mapping):
            obj = [obj]
        if not isinstance(obj, list):
            message = 'Must be a list or a mapping'
            raise CompilationError(message=message)
        with on_key(_KEY_HEADERS):
            return list(map_compile(
                self._description_compiler.compile,
                obj,
            ))
