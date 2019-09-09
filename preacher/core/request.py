"""Request."""

from copy import copy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

import requests

from .datetime import now

from preacher import __version__ as _VERSION


_DEFAULT_HEADERS = {'User-Agent': f'Preacher {_VERSION}'}


@dataclass(frozen=True)
class Response:
    status_code: int
    headers: Mapping[str, str]
    body: str
    request_datetime: datetime


class Request:
    def __init__(
        self,
        path: str = '',
        headers: Mapping[str, str] = {},
        params: Mapping[str, Any] = {},
    ):
        self._path = path
        self._headers = headers
        self._params = params

    def __call__(self, base_url: str) -> Response:
        headers = copy(_DEFAULT_HEADERS)
        headers.update(self._headers)
        request_datetime = now()

        res = requests.get(
            base_url + self._path,
            headers=headers,
            params=self._params,
        )

        return Response(
            status_code=res.status_code,
            headers=res.headers,
            body=res.text,
            request_datetime=request_datetime
        )

    @property
    def path(self) -> str:
        return self._path

    @property
    def headers(self) -> Mapping:
        return self._headers

    @property
    def params(self) -> Mapping:
        return self._params
