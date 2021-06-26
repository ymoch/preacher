"""Response description compilations."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional, List

from preacher.compilation.error import on_key
from preacher.compilation.util.functional import map_compile
from preacher.compilation.util.type import ensure_list, ensure_mapping, or_else
from preacher.core.verification import ResponseDescription, Description, Predicate
from .description import DescriptionCompiler
from .predicate import PredicateCompiler

_KEY_STATUS_CODE = "status_code"
_KEY_HEADERS = "headers"
_KEY_BODY = "body"


@dataclass(frozen=True)
class ResponseDescriptionCompiled:
    status_code: Optional[List[Predicate]] = None
    headers: Optional[List[Description]] = None
    body: Optional[List[Description]] = None

    def replace(
        self,
        other: ResponseDescriptionCompiled,
    ) -> ResponseDescriptionCompiled:
        return ResponseDescriptionCompiled(
            status_code=or_else(other.status_code, self.status_code),
            headers=or_else(other.headers, self.headers),
            body=or_else(other.body, self.body),
        )

    def fix(self) -> ResponseDescription:
        return ResponseDescription(
            status_code=self.status_code,
            headers=self.headers,
            body=self.body,
        )


class ResponseDescriptionCompiler:
    def __init__(
        self,
        predicate: PredicateCompiler,
        description: DescriptionCompiler,
        default: Optional[ResponseDescriptionCompiled] = None,
    ):
        self._predicate = predicate
        self._description = description
        self._default = default or ResponseDescriptionCompiled()

    def compile(self, obj: object) -> ResponseDescriptionCompiled:
        """`obj` should be a mapping."""

        obj = ensure_mapping(obj)
        compiled = self._default

        status_code_obj = obj.get(_KEY_STATUS_CODE)
        if status_code_obj is not None:
            with on_key(_KEY_STATUS_CODE):
                status_code = self._compile_status_code(status_code_obj)
            compiled = replace(compiled, status_code=status_code)

        headers_obj = obj.get(_KEY_HEADERS)
        if headers_obj is not None:
            with on_key(_KEY_HEADERS):
                headers = self._compile_descriptions(headers_obj)
            compiled = replace(compiled, headers=headers)

        body_obj = obj.get(_KEY_BODY)
        if body_obj is not None:
            with on_key(_KEY_BODY):
                body = self._compile_descriptions(body_obj)
            compiled = replace(compiled, body=body)

        return compiled

    def of_default(
        self,
        default: ResponseDescriptionCompiled,
    ) -> ResponseDescriptionCompiler:
        return ResponseDescriptionCompiler(
            predicate=self._predicate,
            description=self._description,
            default=self._default.replace(default),
        )

    def _compile_status_code(self, obj: object) -> List[Predicate]:
        obj = ensure_list(obj)
        return list(map_compile(self._predicate.compile, obj))

    def _compile_descriptions(self, obj: object) -> List[Description]:
        obj = ensure_list(obj)
        return list(map_compile(self._description.compile, obj))
