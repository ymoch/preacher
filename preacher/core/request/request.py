"""Request."""

import uuid
from copy import copy
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum
from typing import Mapping, Optional, Tuple, Union

import requests

from preacher import __version__ as _version
from preacher.core.datetime import now
from preacher.core.status import Status, Statused
from preacher.core.util.error import to_message
from preacher.core.value import ValueContext
from .request_body import RequestBody
from .response import Response, ResponseBody
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

    def __init__(self, id: str, res: requests.Response):
        self._id = id
        self._res = res
        self._body = ResponseBodyWrapper(self._res)

    @property
    def id(self) -> str:
        return self._id

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


@dataclass
class PreparedRequest:
    method: str
    url: str
    headers: Mapping[str, str]
    body: Union[None, str, bytes]


@dataclass(frozen=True)
class ExecutionReport(Statused):
    status: Status = Status.SKIPPED
    starts: datetime = field(default_factory=now)
    request: Optional[PreparedRequest] = None
    message: Optional[str] = None


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

    def execute(
        self,
        base_url: str,
        timeout: Optional[float] = None,
        session: Optional[requests.Session] = None,
    ) -> Tuple[ExecutionReport, Optional[Response]]:
        """
        Executes a request.

        Args:
            base_url: A base URL.
            timeout: The timeout in seconds. ``None`` means no timeout.
            session: A session object to execute.
        Returns:
            A tuple of execution report and response.
            When there is no response, the response will be ``None``.
        """
        if session is None:
            with requests.Session() as new_session:
                return self.execute(
                    base_url=base_url,
                    timeout=timeout,
                    session=new_session,
                )

        starts = now()
        report = ExecutionReport(starts=starts)
        try:
            prepped = self._prepare_request(base_url, starts)
        except Exception as error:
            message = to_message(error)
            report = replace(report, status=Status.FAILURE, message=message)
            return report, None

        report = replace(report, request=PreparedRequest(
            method=prepped.method or '',
            url=prepped.url or '',
            headers=prepped.headers,
            body=prepped.body,
        ))
        try:
            res = session.send(prepped, timeout=timeout)
        except Exception as error:
            message = to_message(error)
            report = replace(report, status=Status.UNSTABLE, message=message)
            return report, None

        report = replace(report, status=Status.SUCCESS)
        response = ResponseWrapper(id=_generate_id(), res=res)
        return report, response

    def _prepare_request(
        self,
        base_url: str,
        starts: datetime,
    ) -> requests.PreparedRequest:
        context = ValueContext(origin_datetime=starts)

        url = base_url + self._path
        headers = copy(_DEFAULT_HEADERS)

        data = None
        if self._body:
            content_type = self._body.content_type
            headers['Content-Type'] = content_type
            data = self._body.resolve(context)

        headers.update(self._headers)
        params = resolve_url_params(self._params, context)

        req = requests.Request(
            method=self._method.value,
            url=url,
            headers=headers,
            params=params,
            data=data,
        )
        return req.prepare()


def _generate_id() -> str:
    return str(uuid.uuid4())
