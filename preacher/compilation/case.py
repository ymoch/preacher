"""Case compilation."""

from __future__ import annotations

from collections.abc import Mapping

from preacher.core.case import Case
from .error import CompilationError, on_key
from .request import RequestCompiler
from .response import ResponseDescriptionCompiler
from .util import compile_bool, compile_optional_str

_KEY_LABEL = 'label'
_KEY_ENABLED = 'enabled'
_KEY_REQUEST = 'request'
_KEY_RESPONSE = 'response'


class CaseCompiler:

    def __init__(
        self,
        request: RequestCompiler,
        response: ResponseDescriptionCompiler,
    ):
        self._request = request
        self._response = response

    def compile(self, obj: object) -> Case:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        label_obj = obj.get(_KEY_LABEL)
        with on_key(_KEY_LABEL):
            label = compile_optional_str(label_obj)

        enabled_obj = obj.get(_KEY_ENABLED, True)
        with on_key(_KEY_ENABLED):
            enabled = compile_bool(enabled_obj)

        request_obj = obj.get(_KEY_REQUEST, {})
        with on_key(_KEY_REQUEST):
            request = self._request.compile(request_obj).to_request()

        response_obj = obj.get(_KEY_RESPONSE)
        with on_key(_KEY_RESPONSE):
            response = self._response.compile(response_obj)

        return Case(
            label=label,
            enabled=enabled,
            request=request,
            response=response,
        )

    def of_default(self, obj: object) -> CaseCompiler:
        request_compiled = self._request.compile(obj)
        response_compiled = self._response.compile(obj)
        return CaseCompiler(
            request=self._request.of_default(request_compiled),
            response=self._response.of_default(response_compiled),
        )
