"""
Test cases, which execute a given request and verify its response
along the given descriptions.
"""

from typing import Optional, List

from preacher.core.request import Request
from preacher.core.verification import Description
from preacher.core.verification import ResponseDescription


class Case:
    """
    Test cases, which execute a given request and verify its response
    along the given descriptions.
    """

    def __init__(
        self,
        label: Optional[str] = None,
        enabled: bool = True,
        conditions: Optional[List[Description]] = None,
        request: Optional[Request] = None,
        response: Optional[ResponseDescription] = None,
    ):
        self._label = label
        self._enabled = enabled
        self._conditions = conditions or []
        self._request = request or Request()
        self._response = response or ResponseDescription()

    @property
    def label(self) -> Optional[str]:
        return self._label

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def conditions(self) -> List[Description]:
        return self._conditions

    @property
    def request(self) -> Request:
        return self._request

    @property
    def response(self) -> ResponseDescription:
        return self._response
