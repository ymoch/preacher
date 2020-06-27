from abc import ABC, abstractmethod
from typing import Any

from preacher.core.scenario.url_param import UrlParams, resolve_url_params


class RequestBody(ABC):

    @property
    @abstractmethod
    def content_type(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def resolve(self, **kwargs) -> Any:
        raise NotImplementedError()


class UrlencodedRequestBody(RequestBody):

    def __init__(self, params: UrlParams):
        self._params = params

    @property
    def content_type(self) -> str:
        return 'application/x-www-form-urlencoded'

    def resolve(self, **kwargs) -> Any:
        return resolve_url_params(self._params, **kwargs)
