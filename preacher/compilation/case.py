"""Case compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

from preacher.core.case import Case
from .error import CompilationError, on_key
from .request import RequestCompiler
from .response import ResponseDescriptionCompiler

_KEY_LABEL = 'label'
_KEY_ENABLED = 'enabled'
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

    def compile(self, obj: object) -> Case:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        label_obj = obj.get(_KEY_LABEL)
        with on_key(_KEY_LABEL):
            label = self._compile_label(label_obj)

        enabled_obj = obj.get(_KEY_ENABLED, True)
        with on_key(_KEY_ENABLED):
            enabled = self._compile_enabled(enabled_obj)

        request_obj = obj.get(_KEY_REQUEST, {})
        with on_key(_KEY_REQUEST):
            request = self._request_compiler.compile(request_obj)

        response_obj = obj.get(_KEY_RESPONSE, {})
        with on_key(_KEY_RESPONSE):
            response = self._response_compiler.compile(response_obj).convert()

        return Case(
            label=label,
            enabled=enabled,
            request=request,
            response=response,
        )

    def of_default(self, obj: Mapping) -> CaseCompiler:
        with on_key(_KEY_REQUEST):
            request_compiler = self._request_compiler.of_default(
                obj.get(_KEY_REQUEST, {})
            )

        with on_key(_KEY_RESPONSE):
            res_compiled = self._response_compiler.compile(
                obj.get(_KEY_RESPONSE, {}),
            )
        res_compiler = self._response_compiler.of_default(res_compiled)
        return CaseCompiler(
            request_compiler=request_compiler,
            response_compiler=res_compiler,
        )

    @staticmethod
    def _compile_label(obj: object) -> Optional[str]:
        """`obj` should be a string or none."""

        if obj is None:
            return obj

        if not isinstance(obj, str):
            raise CompilationError(f'must be a string, given {type(obj)}')
        return obj

    @staticmethod
    def _compile_enabled(obj: object) -> bool:
        """`obj` should be a boolean."""

        if not isinstance(obj, bool):
            raise CompilationError(f'must be a boolean, given {type(obj)}')
        return obj
