from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Mapping, Optional, Callable

from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.url_param import compile_url_params
from preacher.compilation.util import compile_mapping, compile_str
from preacher.core.scenario import (
    RequestBody,
    UrlencodedRequestBody,
    UrlParameters,
)

_KEY_TYPE = 'type'
_KEY_DATA = 'data'


class RequestBodyCompiled(ABC):

    @abstractmethod
    def replace(self, other: RequestBodyCompiled) -> RequestBodyCompiled:
        raise NotImplementedError()

    @abstractmethod
    def compile_and_replace(self, obj: Mapping) -> RequestBodyCompiled:
        raise NotImplementedError()

    @abstractmethod
    def fix(self) -> RequestBody:
        raise NotImplementedError()


@dataclass(frozen=True)
class UrlencodedRequestBodyCompiled(RequestBodyCompiled):
    data: Optional[UrlParameters] = None

    def replace(self, other: RequestBodyCompiled) -> RequestBodyCompiled:
        if not isinstance(other, UrlencodedRequestBodyCompiled):
            return other
        return UrlencodedRequestBodyCompiled(
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


_TYPE_FACTORY_MAP: Mapping[str, Callable[[], RequestBodyCompiled]] = {
    'urlencoded': UrlencodedRequestBodyCompiled,
}


class RequestBodyCompiler:

    def __init__(self, default: Optional[RequestBodyCompiled] = None):
        self._default: RequestBodyCompiled = (
            default or UrlencodedRequestBodyCompiled()
        )

    def compile(self, obj: object) -> RequestBodyCompiled:
        obj = compile_mapping(obj)
        compiled = self._default

        type_obj = obj.get(_KEY_TYPE)
        if type_obj is not None:
            with on_key(_KEY_TYPE):
                key = compile_str(type_obj)
                factory = _TYPE_FACTORY_MAP.get(key)
                if not factory:
                    raise CompilationError(
                        f'Must be in {list(_TYPE_FACTORY_MAP)}'
                        f', but given: {key}'
                    )
            compiled = self._default.replace(factory())

        return compiled.compile_and_replace(obj)

    def of_default(self, default: RequestBodyCompiled) -> RequestBodyCompiler:
        return RequestBodyCompiler(default=self._default.replace(default))
