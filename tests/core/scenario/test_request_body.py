from typing import Any, Optional

from pytest import raises

from preacher.core.scenario.request_body import RequestBody
from preacher.core.scenario.value import ValueContext


def test_request_body():
    class _IncompleteRequestBody(RequestBody):
        @property
        def content_type(self) -> str:
            return super().content_type

        def resolve(self, context: Optional[ValueContext] = None) -> Any:
            return super().resolve(context)

    body = _IncompleteRequestBody()
    with raises(NotImplementedError):
        print(body.content_type)
    with raises(NotImplementedError):
        body.resolve()
