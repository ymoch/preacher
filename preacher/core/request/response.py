"""Response."""

from abc import ABC, abstractmethod
from typing import Mapping


class ResponseBody(ABC):
    @property
    @abstractmethod
    def text(self) -> str:
        ...  # pragma: no cover

    @property
    @abstractmethod
    def content(self) -> bytes:
        ...  # pragma: no cover


class Response(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        ...  # pragma: no cover

    @property
    @abstractmethod
    def elapsed(self) -> float:
        ...  # pragma: no cover

    @property
    @abstractmethod
    def status_code(self) -> int:
        ...  # pragma: no cover

    @property
    @abstractmethod
    def headers(self) -> Mapping[str, str]:
        ...  # pragma: no cover

    @property
    @abstractmethod
    def body(self) -> ResponseBody:
        ...  # pragma: no cover
