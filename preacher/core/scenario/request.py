"""Request."""

import uuid
from copy import copy
from datetime import datetime
from enum import Enum
from typing import Mapping, Optional

import requests

from preacher import __version__ as _version
from preacher.core.datetime import now
from preacher.core.response import Response, ResponseBody
from .request_body import RequestBody
from .url_param import UrlParams, resolve_url_params

_DEFAULT_HEADERS = {'User-Agent': f'Preacher {_version}'}


class Method(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


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
        method: Method = Method.GET,
        path: str = '',
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[UrlParams] = None,
        body: RequestBody = None,
    ):
        self._method = method
        self._path = path
        self._headers = headers or {}
        self._params = params or {}
        self._body = body

    def __call__(
        self,
        base_url: str,
        timeout: Optional[float] = None,
        session: Optional[requests.Session] = None,
    ) -> Response:
        if session is None:
            with requests.Session() as new_session:
                return self.__call__(
                    base_url=base_url,
                    timeout=timeout,
                    session=new_session,
                )

        starts = now()

        url = base_url + self._path
        headers = copy(_DEFAULT_HEADERS)

        data = None
        if self._body:
            content_type = self._body.content_type
            headers['Content-Type'] = content_type
            data = self._body.resolve(origin_datetime=starts)

        headers.update(self._headers)
        params = resolve_url_params(self._params, origin_datetime=starts)

        res = session.request(
            str(self._method.value),
            url,
            headers=headers,
            params=params,  # type: ignore
            data=data,
            timeout=timeout,
        )
        return ResponseWrapper(id=str(uuid.uuid4()), starts=starts, res=res)

    @property
    def method(self) -> Method:
        return self._method

    @property
    def path(self) -> str:
        return self._path

    @property
    def headers(self) -> Mapping:
        return self._headers

    @property
    def params(self) -> UrlParams:
        return self._params

    @property
    def body(self) -> Optional[RequestBody]:
        return self._body
