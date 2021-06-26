from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Mapping, Optional, Callable

from preacher.compilation.argument import Arguments, inject_arguments
from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util.type import ensure_str, ensure_mapping
from preacher.core.request import (
    RequestBody,
    UrlencodedRequestBody,
    UrlParams,
    JsonRequestBody,
)
from .url_param import compile_url_params

_NOT_SPECIFIED = object()
_KEY_TYPE = "type"
_KEY_DATA = "data"


class RequestBodyCompiled(ABC):
    @abstractmethod
    def replace(self, other: RequestBodyCompiled) -> RequestBodyCompiled:
        ...  # pragma: no cover

    @abstractmethod
    def compile_and_replace(self, obj: Mapping) -> RequestBodyCompiled:
        ...  # pragma: no cover

    @abstractmethod
    def fix(self) -> RequestBody:
        ...  # pragma: no cover


@dataclass(frozen=True)
class UrlencodedRequestBodyCompiled(RequestBodyCompiled):
    data: Optional[UrlParams] = None

    def replace(self, other: RequestBodyCompiled) -> RequestBodyCompiled:
        if not isinstance(other, UrlencodedRequestBodyCompiled):
            return other
        return replace(
            self,
            data=other.data if other.data is not None else self.data,
        )

    def compile_and_replace(self, obj: Mapping) -> RequestBodyCompiled:
        compiled = self

        data_obj = obj.get(_KEY_DATA)
        if data_obj is not None:
            with on_key(_KEY_DATA):
                data = compile_url_params(data_obj)
            compiled = replace(self, data=data)

        return compiled

    def fix(self) -> RequestBody:
        return UrlencodedRequestBody(params=self.data or {})


@dataclass(frozen=True)
class JsonRequestBodyCompiled(RequestBodyCompiled):
    data: object = _NOT_SPECIFIED

    def replace(self, other: RequestBodyCompiled) -> RequestBodyCompiled:
        if not isinstance(other, JsonRequestBodyCompiled):
            return other
        return replace(
            self,
            data=other.data if other.data is not _NOT_SPECIFIED else self.data,
        )

    def compile_and_replace(self, obj: Mapping) -> RequestBodyCompiled:
        compiled = self

        if _KEY_DATA in obj:
            data = obj[_KEY_DATA]
            compiled = replace(self, data=data)

        return compiled

    def fix(self) -> RequestBody:
        return JsonRequestBody(
            data=self.data if self.data is not _NOT_SPECIFIED else None,
        )


_TYPE_FACTORY_MAP: Mapping[str, Callable[[], RequestBodyCompiled]] = {
    "urlencoded": UrlencodedRequestBodyCompiled,
    "json": JsonRequestBodyCompiled,
}


class RequestBodyCompiler:
    def __init__(self, default: Optional[RequestBodyCompiled] = None):
        self._default: RequestBodyCompiled = default or UrlencodedRequestBodyCompiled()

    def compile(
        self,
        obj: object,
        arguments: Optional[Arguments] = None,
    ) -> RequestBodyCompiled:
        """
        Compiles an object into an intermediate request body.

        Args:
            obj: A compiled object, which should be a mapping.
            arguments: Arguments to inject.
        Returns:
            The result of compilation.
        Raises:
            CompilationError: when compilation fails.
        """

        obj = inject_arguments(obj, arguments)
        obj = ensure_mapping(obj)
        compiled = self._default

        type_obj = obj.get(_KEY_TYPE)
        if type_obj is not None:
            with on_key(_KEY_TYPE):
                key = ensure_str(type_obj)
                factory = _TYPE_FACTORY_MAP.get(key)
                if not factory:
                    raise CompilationError(
                        f"Must be in {list(_TYPE_FACTORY_MAP)}" f", but given: {key}"
                    )
            compiled = self._default.replace(factory())

        return compiled.compile_and_replace(obj)

    def of_default(self, default: RequestBodyCompiled) -> RequestBodyCompiler:
        """
        Creates a new compiler
        that is configured of the default request body.

        Args:
            default: A default request body.
        Returns:
            A new compiler.
        """

        return RequestBodyCompiler(default=self._default.replace(default))
