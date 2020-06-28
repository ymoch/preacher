import json
from abc import ABC, abstractmethod
from typing import Any

from preacher.core.functional import recursive_map
from preacher.core.interpretation.value import Value
from preacher.core.scenario.url_param import UrlParams, resolve_url_params
from preacher.core.scenario.util.serialization import to_serializable_value


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


class JsonRequestBody(RequestBody):

    def __init__(self, data: object):
        self._data = data

    @property
    def content_type(self) -> str:
        return 'application/json'

    def resolve(self, **kwargs) -> Any:
        def _resolve_value(obj: object) -> object:
            if isinstance(obj, Value):
                return recursive_map(
                    _resolve_value,
                    _resolve_value(obj.apply_context(**kwargs)),
                )
            return to_serializable_value(obj)

        resolved = recursive_map(_resolve_value, self._data)
        return json.dumps(resolved, separators=(',', ':'))
