"""Request."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import requests


@dataclass
class Response:
    status_code: int
    headers: Mapping
    body: str


class Request:
    """
    >>> request = Request(path='/path', params={'key': 'value'})
    >>> request.path
    '/path'
    >>> request.params
    {'key': 'value'}

    >>> from unittest.mock import MagicMock, patch
    >>> inner_response = MagicMock(
    ...     requests.Response,
    ...     status_code=402,
    ...     headers={'header-key': 'header-value'},
    ...     text='text',
    ... )
    >>> with patch('requests.get', return_value=inner_response) as mock:
    ...     response = request('base-url')
    ...     mock.call_args
    call('base-url/path', params={'key': 'value'})
    >>> response.status_code
    402
    >>> response.headers
    {'header-key': 'header-value'}
    >>> response.body
    'text'
    """
    def __init__(self, path: str, params: Mapping) -> None:
        self._path = path
        self._params = params

    def __call__(self, base_url: str) -> Response:
        res = requests.get(
            base_url + self._path,
            params=self._params,
        )
        return Response(
            status_code=res.status_code,
            headers=res.headers,
            body=res.text,
        )

    @property
    def path(self: Request) -> str:
        return self._path

    @property
    def params(self: Request) -> Mapping:
        return self._params
