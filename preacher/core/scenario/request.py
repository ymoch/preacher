"""Request."""

import uuid
from copy import copy
from datetime import datetime
from typing import List, Mapping, Optional, Union

import requests

from preacher import __version__ as _version
from preacher.core.datetime import now
from preacher.core.response import Response, ResponseBody
from .type import ScalarType

_DEFAULT_HEADERS = {'User-Agent': f'Preacher {_version}'}

ParameterValue = Union[None, ScalarType, List[Optional[ScalarType]]]
Parameters = Union[None, ScalarType, Mapping[str, ParameterValue]]


class ResponseBodyWrapper(ResponseBody):

    def __init__(self, res: requests.Response):
        self._res = res

    @property
    def text(self) -> str:
        return self._res.text

    @property
    def content(self) -> bytes:
        return self._res.content


class ResponseWrapper(Response):

    def __init__(self, id: str, starts: datetime, res: requests.Response):
        self._id = id
        self._starts = starts
        self._res = res
        self._body = ResponseBodyWrapper(self._res)

    @property
    def id(self) -> str:
        return self._id

    @property
    def starts(self) -> datetime:
        return self._starts

    @property
    def elapsed(self) -> float:
        return self._res.elapsed.total_seconds()

    @property
    def status_code(self) -> int:
        return self._res.status_code

    @property
    def headers(self) -> Mapping[str, str]:
        # Convert to the normal dictionary to adapt jq.
        # Names are converted to lower case to normalize.
        return {
            name.lower(): value for (name, value) in self._res.headers.items()
        }

    @property
    def body(self) -> ResponseBody:
        return self._body


class Request:

    def __init__(
        self,
        path: str = '',
        headers: Optional[Mapping[str, str]] = None,
        params: Parameters = None,
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
        starts = now()

        res = requests.get(
            base_url + self._path,
            headers=headers,
            params=self._params,  # type: ignore
            timeout=timeout,
        )
        return ResponseWrapper(id=str(uuid.uuid4()), starts=starts, res=res)

    @property
    def path(self) -> str:
        return self._path

    @property
    def headers(self) -> Mapping:
        return self._headers

    @property
    def params(self) -> Parameters:
        return self._params
