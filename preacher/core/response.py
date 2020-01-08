from abc import ABC, abstractmethod
from datetime import datetime
from typing import Mapping


class ResponseBody(ABC):

    @property
    @abstractmethod
    def text(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def content(self) -> bytes:
        raise NotImplementedError()


class Response(ABC):

    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def starts(self) -> datetime:
        raise NotImplementedError()

    @property
    @abstractmethod
    def elapsed(self) -> float:
        raise NotImplementedError()

    @property
    @abstractmethod
    def status_code(self) -> int:
        raise NotImplementedError()

    @property
    @abstractmethod
    def headers(self) -> Mapping[str, str]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def body(self) -> ResponseBody:
        raise NotImplementedError()
