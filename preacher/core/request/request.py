"""Request."""

from enum import Enum
from typing import Mapping, Optional

from .request_body import RequestBody
from .url_param import UrlParams


class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class Request:
    def __init__(
        self,
        method: Method = Method.GET,
        path: str = "",
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[UrlParams] = None,
        body: Optional[RequestBody] = None,
    ):
        self._method = method
        self._path = path
        self._headers = headers or {}
        self._params = params or {}
        self._body = body

    @property
    def method(self) -> Method:
        return self._method

    @property
    def path(self) -> str:
        return self._path

    @property
    def headers(self) -> Mapping[str, str]:
        return self._headers

    @property
    def params(self) -> UrlParams:
        return self._params

    @property
    def body(self) -> Optional[RequestBody]:
        return self._body
