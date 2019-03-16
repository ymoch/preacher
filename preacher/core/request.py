"""Request."""

import requests

from .verification import Verification


class Request:
    def __init__(self, path: str, query: dict) -> None:
        self._path = path
        self._query = query

    def __call__(self, base_url: str) -> Verification:
        try:
            requests.get(
                base_url + self._path,
                query=self._query,
            )
        except requests.HTTPError as error:
            return Verification.of_error(error)

        return Verification.succeed()
