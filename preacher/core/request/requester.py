import uuid
from copy import copy
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Mapping, Union, Optional, Tuple

import requests

from preacher import __version__ as _version
from preacher.core.datetime import now
from preacher.core.status import Statused, Status
from preacher.core.util.error import to_message
from preacher.core.value import ValueContext
from .request import Request
from .response import Response, ResponseBody
from .url_param import resolve_url_params

_DEFAULT_HEADERS = {"User-Agent": f"Preacher {_version}"}


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
        return {name.lower(): value for (name, value) in self._res.headers.items()}

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


class Requester:
    def __init__(
        self,
        base_url: str = "",
        timeout: Optional[float] = None,
    ):
        """
        Args:
            base_url: A base URL.
            timeout: The timeout in seconds. ``None`` means no timeout.
        """
        self._base_url = base_url
        self._timeout = timeout

    @property
    def base_url(self) -> str:
        return self._base_url

    def execute(
        self,
        request: Request,
        session: Optional[requests.Session] = None,
    ) -> Tuple[ExecutionReport, Optional[Response]]:
        """
        Executes a request.

        Args:
            request: A request.
            session: A session object to execute.
        Returns:
            A tuple of execution report and response.
            When there is no response, the response will be ``None``.
        """
        if session is None:
            with requests.Session() as new_session:
                return self.execute(request, session=new_session)

        starts = now()
        report = ExecutionReport(starts=starts)
        try:
            prepped = self._prepare_request(request, starts)
            proxies = session.rebuild_proxies(prepped, proxies=None)
        except Exception as error:
            message = to_message(error)
            report = replace(report, status=Status.FAILURE, message=message)
            return report, None

        report = replace(
            report,
            request=PreparedRequest(
                method=prepped.method or "",
                url=prepped.url or "",
                headers=prepped.headers,
                body=prepped.body,
            ),
        )

        try:
            res = session.send(prepped, proxies=proxies, timeout=self._timeout)
        except Exception as error:
            message = to_message(error)
            report = replace(report, status=Status.UNSTABLE, message=message)
            return report, None

        report = replace(report, status=Status.SUCCESS)
        response = ResponseWrapper(id=_generate_id(), res=res)
        return report, response

    def _prepare_request(
        self,
        request: Request,
        starts: datetime,
    ) -> requests.PreparedRequest:
        context = ValueContext(origin_datetime=starts)

        url = self._base_url + request.path
        headers = copy(_DEFAULT_HEADERS)

        data = None
        if request.body:
            content_type = request.body.content_type
            headers["Content-Type"] = content_type
            data = request.body.resolve(context)

        headers.update(request.headers)
        params = resolve_url_params(request.params, context)

        req = requests.Request(
            method=request.method.value,
            url=url,
            headers=headers,
            params=params,
            data=data,
        )
        return req.prepare()


def _generate_id() -> str:
    return str(uuid.uuid4())
