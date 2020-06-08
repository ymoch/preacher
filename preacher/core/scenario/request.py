"""Request."""

import uuid
from copy import copy
from datetime import datetime
from typing import Any, List, Mapping, Optional, Union

import requests

from preacher import __version__ as _version
from preacher.core.datetime import now
from preacher.core.interpretation.value import Value
from preacher.core.response import Response, ResponseBody

_DEFAULT_HEADERS = {'User-Agent': f'Preacher {_version}'}

ParameterRawValue = Union[None, bool, int, float, str]
ParameterValue = Union[ParameterRawValue, Value[ParameterRawValue]]
Parameter = Union[ParameterValue, List[ParameterValue]]
Parameters = Union[str, Mapping[str, Parameter]]
ResolvedParameter = Union[ParameterRawValue, List[ParameterRawValue]]


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


def resolve_param_value(value: ParameterValue, **kwargs) -> ParameterRawValue:
    if isinstance(value, Value):
        return value.apply_context(**kwargs)
    return value


def resolve_param(param: Parameter, **kwargs) -> ResolvedParameter:
    if isinstance(param, list):
        return [resolve_param_value(value, **kwargs) for value in param]
    return resolve_param_value(param)


def resolve_params(params: Parameters, **kwargs) -> Any:
    if isinstance(params, str):
        return params
    return {
        key: resolve_param(param, **kwargs)
        for (key, param) in params.items()
    }


class Request:

    def __init__(
        self,
        path: str = '',
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Parameters] = None,
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
            params=resolve_params(self._params, origin=starts),
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
