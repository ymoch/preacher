from typing import Mapping

from pytest import raises

from preacher.core.request import Response, ResponseBody


def test_incomplete_response_body():

    class _IncompleteResponseBody(ResponseBody):

        @property
        def text(self) -> str:
            return super().text

        @property
        def content(self) -> bytes:
            return super().content

    body = _IncompleteResponseBody()
    with raises(NotImplementedError):
        print(body.text)
    with raises(NotImplementedError):
        print(body.content)


def test_incomplete_response():

    class _IncompleteResponse(Response):

        @property
        def id(self) -> str:
            return super().id

        @property
        def elapsed(self) -> float:
            return super().elapsed

        @property
        def status_code(self) -> int:
            return super().status_code

        @property
        def headers(self) -> Mapping[str, str]:
            return super().headers

        @property
        def body(self) -> ResponseBody:
            return super().body

    response = _IncompleteResponse()
    with raises(NotImplementedError):
        print(response.id)
    with raises(NotImplementedError):
        print(response.elapsed)
    with raises(NotImplementedError):
        print(response.status_code)
    with raises(NotImplementedError):
        print(response.headers)
    with raises(NotImplementedError):
        print(response.body)
