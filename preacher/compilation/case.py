"""Case compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional

from preacher.core.case import Case
from .error import CompilationError, NamedNode
from .request import RequestCompiler
from .response_description import ResponseDescriptionCompiler
from .util import run_on_key


_KEY_LABEL = 'label'
_KEY_REQUEST = 'request'
_KEY_RESPONSE = 'response'


class CaseCompiler:

    def __init__(
        self,
        request_compiler: Optional[RequestCompiler] = None,
        response_compiler: Optional[ResponseDescriptionCompiler] = None
    ):
        self._request_compiler = request_compiler or RequestCompiler()
        self._response_compiler = (
            response_compiler or ResponseDescriptionCompiler()
        )

    @property
    def request_compiler(self) -> RequestCompiler:
        return self._request_compiler

    def compile(self, obj: Any) -> Case:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        label = obj.get(_KEY_LABEL)
        if label is not None and not isinstance(label, str):
            raise CompilationError(
                message=f'Case.{_KEY_LABEL} must be a string',
                path=[NamedNode(_KEY_LABEL)],
            )

        request = run_on_key(
            _KEY_REQUEST,
            self._request_compiler.compile,
            obj.get(_KEY_REQUEST, {}),
        )
        response_description = run_on_key(
            _KEY_RESPONSE,
            self._response_compiler.compile,
            obj.get(_KEY_RESPONSE, {}),
        ).convert()
        return Case(
            label=label,
            request=request,
            response_description=response_description,
        )

    def of_default(self, obj: Mapping) -> CaseCompiler:
        request_compiler = run_on_key(
            _KEY_REQUEST,
            self._request_compiler.of_default,
            obj.get(_KEY_REQUEST, {}),
        )

        res_compiled = run_on_key(
            _KEY_RESPONSE,
            self._response_compiler.compile,
            obj.get(_KEY_RESPONSE, {}),
        )
        res_compiler = self._response_compiler.of_default(res_compiled)
        return CaseCompiler(
            request_compiler=request_compiler,
            response_compiler=res_compiler,
        )
