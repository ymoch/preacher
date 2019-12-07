"""Request."""

import uuid
from copy import copy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Optional

import requests

from preacher import __version__ as _version
from .datetime import now

_DEFAULT_HEADERS = {'User-Agent': f'Preacher {_version}'}


@dataclass(frozen=True)
class Response:
    id: str
    elapsed: float
    status_code: int
    headers: Mapping[str, str]
    body: str
    request_datetime: datetime


class Request:

    def __init__(
        self,
        path: str = '',
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, Any]] = None,
    ):
        self._path = path
        self._headers = headers or {}
        self._params = params or {}

    def __call__(
        self,
        base_url: str,
        timeout: Optional[float] = None,
    ) -> Response:
        headers = copy(_DEFAULT_HEADERS)
        headers.update(self._headers)
        request_datetime = now()

        res = requests.get(
            base_url + self._path,
            headers=headers,
            params=self._params,
            timeout=timeout,
        )

        return Response(
            id=str(uuid.uuid4()),
            elapsed=res.elapsed.total_seconds(),
            status_code=res.status_code,
            headers={
                # Convert to the normal dictionary to adapt jq.
                # Names are converted to lower case to normalize.
                name.lower(): value for (name, value) in res.headers.items()
            },
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
