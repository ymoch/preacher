from typing import Any

from pytest import raises

from preacher.core.scenario.request_body import RequestBody


def test_request_body():
    class _IncompleteRequestBody(RequestBody):
        @property
        def content_type(self) -> str:
            return super().content_type

        @property
        def resolve(self, **kwargs) -> Any:
            return super().resolve(**kwargs)

    body = _IncompleteRequestBody()
    with raises(NotImplementedError):
        print(body.content_type)
    with raises(NotImplementedError):
        body.resolve(foo='bar')
