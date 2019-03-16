"""Request."""

from dataclasses import dataclass
from typing import Mapping

import requests


@dataclass
class Response:
    status_code: int
    headers: Mapping[str, str]
    body: str


class Request:
    def __init__(self, path: str, query: dict) -> None:
        self._path = path
        self._query = query

    def __call__(self, base_url: str) -> Response:
        res = requests.get(
            base_url + self._path,
            query=self._query,
        )
        return Response(
            status_code=res.status_code,
            headers=res.headers,
            body=res.text,
        )
