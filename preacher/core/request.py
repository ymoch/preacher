"""Request."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

import requests

from .datetime import now

from preacher import __version__ as _VERSION


_DEFAULT_HEADERS = {
    'User-Agent': f'Preacher {_VERSION}'
}


@dataclass(frozen=True)
class Response:
    status_code: int
    headers: Mapping
    body: str
    request_datetime: datetime


class Request:
    def __init__(self, path: str, params: Mapping):
        self._path = path
        self._params = params

    def __call__(self, base_url: str) -> Response:
        request_datetime = now()

        res = requests.get(
            base_url + self._path,
            headers=_DEFAULT_HEADERS,
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
    def params(self) -> Mapping:
        return self._params
