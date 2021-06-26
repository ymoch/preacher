"""Request compilation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from preacher.compilation.argument import Argument, Arguments, inject_arguments
from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util.type import ensure_str, ensure_mapping, or_else
from preacher.core.request import Request, Method, UrlParams
from .request_body import RequestBodyCompiled, RequestBodyCompiler
from .url_param import compile_url_params

_KEY_METHOD = "method"
_KEY_PATH = "path"
_KEY_HEADERS = "headers"
_KEY_PARAMS = "params"
_KEY_BODY = "body"

_METHOD_MAP = {method.name: method for method in Method}


@dataclass(frozen=True)
class RequestCompiled:
    method: Optional[Method] = None
    path: Optional[str] = None
    headers: Optional[Mapping[str, str]] = None
    params: Optional[UrlParams] = None
    body: Optional[RequestBodyCompiled] = None

    def replace(self, other: RequestCompiled) -> RequestCompiled:
        return RequestCompiled(
            method=or_else(other.method, self.method),
            path=or_else(other.path, self.path),
            headers=or_else(other.headers, self.headers),
            params=other.params if other.params is not None else self.params,
            body=or_else(other.body, self.body),
        )

    def fix(self) -> Request:
        return Request(
            method=or_else(self.method, Method.GET),
            path=or_else(self.path, ""),
            headers=self.headers,
            params=self.params,
            body=self.body.fix() if self.body else None,
        )


class RequestCompiler:
    def __init__(
        self,
        body: RequestBodyCompiler,
        default: RequestCompiled = None,
    ):
        self._body = body
        self._default = default or RequestCompiled()

    def compile(
        self,
        obj: object,
        arguments: Optional[Arguments] = None,
    ) -> RequestCompiled:
        """
        Compiles an object into an intermediate request.

        Args:
            obj: A compiled object, which should be a mapping or a string.
            arguments: Arguments to inject.
        Returns:
            The result of compilation.
        Raises:
            CompilationError: when compilation fails.
        """
        if isinstance(obj, Argument):
            obj = inject_arguments(obj, arguments)

        if isinstance(obj, str):
            return self.compile({_KEY_PATH: obj}, arguments)

        obj = ensure_mapping(obj)
        compiled = self._default

        method_obj = obj.get(_KEY_METHOD)
        if method_obj is not None:
            with on_key(_KEY_METHOD):
                method_obj = inject_arguments(method_obj, arguments)
                method = _compile_method(method_obj)
            compiled = replace(compiled, method=method)

        path_obj = obj.get(_KEY_PATH)
        if path_obj is not None:
            with on_key(_KEY_PATH):
                path_obj = inject_arguments(path_obj, arguments)
                path = ensure_str(path_obj)
            compiled = replace(compiled, path=path)

        headers_obj = obj.get(_KEY_HEADERS)
        if headers_obj is not None:
            with on_key(_KEY_HEADERS):
                headers_obj = inject_arguments(headers_obj, arguments)
                headers = _compile_headers(headers_obj)
            compiled = replace(compiled, headers=headers)

        params_obj = obj.get(_KEY_PARAMS)
        if params_obj is not None:
            with on_key(_KEY_PARAMS):
                params = compile_url_params(params_obj, arguments)
            compiled = replace(compiled, params=params)

        body_obj = obj.get(_KEY_BODY)
        if body_obj is not None:
            with on_key(_KEY_BODY):
                body = self._body.compile(body_obj, arguments)
            compiled = replace(compiled, body=body)

        return compiled

    def of_default(self, default: RequestCompiled) -> RequestCompiler:
        body = self._body
        if default.body:
            body = body.of_default(default.body)

        return RequestCompiler(body=body, default=self._default.replace(default))


def _compile_method(obj: object) -> Method:
    key = ensure_str(obj).upper()
    method = _METHOD_MAP.get(key)
    if not method:
        message = f"Must be in {list(_METHOD_MAP)}, but given: {obj}"
        raise CompilationError(message)
    return method


def _compile_headers(obj: object) -> Mapping[str, str]:
    obj = ensure_mapping(obj)
    items = (_compile_header_item(k, v) for (k, v) in obj.items())
    return dict(filter(None, items))


def _compile_header_item(key: object, value: object) -> Optional[Tuple[str, str]]:
    if value is None:
        return None
    return ensure_str(key), ensure_str(value)
