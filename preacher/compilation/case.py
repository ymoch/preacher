"""Case compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

from preacher.core.case import Case
from .error import CompilationError, on_key
from .request import RequestCompiler
from .response import ResponseDescriptionCompiler
from .util import compile_bool, compile_str

_KEY_LABEL = 'label'
_KEY_ENABLED = 'enabled'
_KEY_REQUEST = 'request'
_KEY_RESPONSE = 'response'


class CaseCompiler:

    def __init__(
        self,
        request: RequestCompiler,
        response: ResponseDescriptionCompiler,
        default: Optional[Case] = None,
    ):
        self._request = request
        self._response = response
        self._default = default or Case()

    def compile(self, obj: object) -> Case:
        """`obj` should be a mapping."""

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping')

        label = self._default.label
        label_obj = obj.get(_KEY_LABEL)
        if label_obj is not None:
            with on_key(_KEY_LABEL):
                label = compile_str(label_obj)

        enabled = self._default.enabled
        enabled_obj = obj.get(_KEY_ENABLED)
        if enabled_obj is not None:
            with on_key(_KEY_ENABLED):
                enabled = compile_bool(enabled_obj)

        request = self._default.request
        request_obj = obj.get(_KEY_REQUEST)
        if request_obj is not None:
            with on_key(_KEY_REQUEST):
                request = self._request.compile(request_obj)

        response = self._default.response
        response_obj = obj.get(_KEY_RESPONSE)
        if response_obj is not None:
            with on_key(_KEY_RESPONSE):
                response = self._response.compile(response_obj)

        return Case(
            label=label,
            enabled=enabled,
            request=request,
            response=response,
        )

    def of_default(self, default: Case) -> CaseCompiler:
        return CaseCompiler(
            request=self._request.of_default(default.request),
            response=self._response.of_default(default.response),
            default=default,
        )
