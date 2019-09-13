"""Case compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional, Union

from preacher.core.case import Case
from .error import CompilationError
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
                path=[_KEY_LABEL],
            )

        request = run_on_key(
            _KEY_REQUEST,
            self._request_compiler.compile,
            _extract_request(obj)
        )
        response_description = run_on_key(
            _KEY_RESPONSE,
            self._response_compiler.compile,
            _extract_response(obj),
        )
        return Case(
            label=label,
            request=request,
            response_description=response_description,
        )

    def of_default(self, obj: Mapping) -> CaseCompiler:
        request_compiler = run_on_key(
            _KEY_REQUEST,
            self._request_compiler.of_default,
            _extract_request(obj),
        )
        return CaseCompiler(request_compiler=request_compiler)


def _extract_request(obj: Any) -> Union[Mapping, str]:
    target = obj.get(_KEY_REQUEST, {})
    if not isinstance(target, Mapping) and not isinstance(target, str):
        raise CompilationError(
            message='must be a string or a mapping',
            path=[_KEY_REQUEST],
        )
    return target


def _extract_response(obj: Any) -> Mapping:
    target = obj.get('response', {})
    if not isinstance(target, Mapping):
        raise CompilationError('must be a mapping', path=[_KEY_RESPONSE])
    return target
