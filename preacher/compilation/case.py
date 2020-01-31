"""Case compilation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

from preacher.core.scenario import Case
from .error import on_key
from .request import RequestCompiler, RequestCompiled
from .response_description import (
    ResponseDescriptionCompiled,
    ResponseDescriptionCompiler,
)
from .util import compile_bool, compile_optional_str, or_else, compile_mapping

_KEY_LABEL = 'label'
_KEY_ENABLED = 'enabled'
_KEY_REQUEST = 'request'
_KEY_RESPONSE = 'response'


@dataclass(frozen=True)
class CaseCompiled:
    label: Optional[str] = None
    enabled: Optional[bool] = None
    request: Optional[RequestCompiled] = None
    response: Optional[ResponseDescriptionCompiled] = None

    def replace(self, other: CaseCompiled) -> CaseCompiled:
        return CaseCompiled(
            label=or_else(other.label, self.label),
            enabled=or_else(other.enabled, self.enabled),
            request=or_else(other.request, self.request),
            response=or_else(other.response, self.response),
        )

    def fix(self) -> Case:
        return Case(
            label=self.label,
            enabled=or_else(self.enabled, True),
            request=self.request.fix() if self.request else None,
            response=self.response.fix() if self.response else None,
        )


class CaseCompiler:

    def __init__(
        self,
        request: RequestCompiler,
        response: ResponseDescriptionCompiler,
        default: Optional[CaseCompiled] = None
    ):
        self._request = request
        self._response = response
        self._default = default or CaseCompiled()

    def compile_fixed(self, obj: object) -> Case:
        """
        Compile a given case object into a fixed case.

        Args:
            obj: A compiled object.
        Returns:
            The result of compilation.
        Raises:
            CompilationError: when compilation fails.
        """
        return self.compile(obj).fix()

    def compile_default(self, obj: object) -> CaseCompiler:
        """
        Compile a given case object and replace the default value with it.

        Args:
            obj: A compiled object.
        Returns:
            The replaced compiler.
        Raises:
            CompilationError: when compilation fails.
        """
        default = self.compile(obj)
        return self.of_default(default)

    def compile(self, obj: object) -> CaseCompiled:
        """`obj` should be a mapping."""

        obj = compile_mapping(obj)
        compiled = self._default

        label_obj = obj.get(_KEY_LABEL)
        with on_key(_KEY_LABEL):
            label = compile_optional_str(label_obj)
            # `label` is always replaced.
            compiled = replace(compiled, label=label)

        enabled_obj = obj.get(_KEY_ENABLED)
        if enabled_obj is not None:
            with on_key(_KEY_ENABLED):
                enabled = compile_bool(enabled_obj)
            compiled = replace(compiled, enabled=enabled)

        request_obj = obj.get(_KEY_REQUEST)
        if request_obj is not None:
            with on_key(_KEY_REQUEST):
                request = self._request.compile(request_obj)
            compiled = replace(compiled, request=request)

        response_obj = obj.get(_KEY_RESPONSE)
        if response_obj is not None:
            with on_key(_KEY_RESPONSE):
                response = self._response.compile(response_obj)
            compiled = replace(compiled, response=response)

        return compiled

    def of_default(self, default: CaseCompiled) -> CaseCompiler:
        request = self._request
        if default.request:
            request = self._request.of_default(default.request)

        response = self._response
        if default.response:
            response = self._response.of_default(default.response)

        return CaseCompiler(
            request=request,
            response=response,
            default=self._default.replace(default),
        )
