import uuid
from datetime import timedelta
from typing import Optional
from unittest.mock import NonCallableMock, NonCallableMagicMock, sentinel

import requests
from pytest import fixture

from preacher.core.context import Context
from preacher.core.request import UrlParams
from preacher.core.request.request import Request, Method
from preacher.core.request.request_body import RequestBody
from preacher.core.request.requester import Requester, ResponseWrapper
from preacher.core.request.url_param import ResolvedUrlParams
from preacher.core.status import Status

PKG = "preacher.core.request.requester"


@fixture
def session():
    response = NonCallableMock(requests.Response)
    response.elapsed = timedelta(seconds=1.23)
    response.status_code = 402
    response.headers = {"Header-Name": "Header-Value"}
    response.text = sentinel.text
    response.content = sentinel.content

    session = NonCallableMagicMock(requests.Session)
    session.__enter__.return_value = session
    session.rebuild_proxies.return_value = sentinel.proxies
    session.send.return_value = response
    return session


@fixture
def body():
    mock = NonCallableMock(RequestBody)
    mock.content_type = "text/plain"
    mock.resolve.return_value = {"x": "y", "name": ["東", "京"]}
    return mock


def test_default_request(mocker, session):
    mocker.patch("requests.Session", return_value=session)

    requester = Requester(base_url="http://base-url.org")
    assert requester.base_url == "http://base-url.org"

    request = Request()
    report, _res = requester.execute(request)
    assert report.request.method == "GET"
    assert report.request.url == "http://base-url.org/"
    assert report.request.headers["User-Agent"].startswith("Preacher")
    assert report.request.body is None

    args, kwargs = session.send.call_args
    prepped = args[0]
    assert isinstance(prepped, requests.PreparedRequest)
    assert prepped.method == "GET"
    assert prepped.url == "http://base-url.org/"
    assert prepped.headers["User-Agent"].startswith("Preacher")
    assert prepped.body is None
    assert kwargs["proxies"] is sentinel.proxies
    assert kwargs["timeout"] is None

    session.__enter__.assert_called_once()
    session.__exit__.assert_called_once()


def test_when_request_preparation_fails(mocker, session):
    mocker.patch(f"{PKG}.now", return_value=sentinel.now)

    req = NonCallableMock(requests.Request)
    req.prepare.side_effect = RuntimeError("msg")
    mocker.patch("requests.Request", return_value=req)

    request = Request()
    requester = Requester("base-url")
    execution, response = requester.execute(request, session=session)

    assert execution.status is Status.FAILURE
    assert execution.starts is sentinel.now
    assert execution.request is None
    assert execution.message == "RuntimeError: msg"

    session.rebuild_proxies.assert_not_called()
    session.send.assert_not_called()


def test_when_proxy_building_fails(mocker, session):
    session.rebuild_proxies.side_effect = RuntimeError("message")

    req = NonCallableMock(requests.Request)
    req.prepare.return_value = sentinel.prepped
    mocker.patch("requests.Request", return_value=req)

    request = Request()
    requester = Requester("http://base-url")
    execution, response = requester.execute(request, session=session)

    assert execution.status is Status.FAILURE
    assert execution.request is None
    assert execution.message == "RuntimeError: message"

    session.rebuild_proxies.assert_called_once_with(sentinel.prepped, proxies=None)
    session.send.assert_not_called()


def test_when_request_fails(mocker, session):
    mocker.patch(f"{PKG}.now", return_value=sentinel.now)
    session.send.side_effect = RuntimeError("msg")

    request = Request()
    requester = Requester("http://base.org/")
    execution, response = requester.execute(request, session=session)

    assert execution.status is Status.UNSTABLE
    assert execution.starts is sentinel.now
    assert execution.request.method == "GET"
    assert execution.request.url == "http://base.org/"
    assert execution.request.headers["User-Agent"].startswith("Preacher")
    assert execution.request.body is None
    assert execution.message == "RuntimeError: msg"

    session.rebuild_proxies.assert_called_once()
    session.send.assert_called_once()


def test_when_request_succeeds(mocker, session, body):
    now = mocker.patch(f"{PKG}.now", return_value=sentinel.now)

    uuid_obj = NonCallableMagicMock(uuid.UUID)
    uuid_obj.__str__.return_value = "id"
    uuid4 = mocker.patch("uuid.uuid4", return_value=uuid_obj)

    def _resolve_url_params(
        params: UrlParams,
        context: Optional[Context] = None,
    ) -> ResolvedUrlParams:
        assert params is sentinel.params
        assert context == {"foo": "bar", "starts": sentinel.now}
        return {"name": "京", "a": ["b", "c"]}

    resolve_params = mocker.patch(f"{PKG}.resolve_url_params", side_effect=_resolve_url_params)

    request = Request(
        method=Method.POST,
        path="/path",
        headers={"k1": "v1"},
        params=sentinel.params,
        body=body,
    )
    requester = Requester("https://a.com", timeout=5.0)
    report, response = requester.execute(request, session=session, context={"foo": "bar"})
    assert report.status is Status.SUCCESS
    assert report.request
    assert report.request.method == "POST"
    assert report.request.url == "https://a.com/path?name=%E4%BA%AC&a=b&a=c"
    assert report.request.headers["Content-Type"] == "text/plain"
    assert report.request.headers["User-Agent"].startswith("Preacher")
    assert report.request.headers["k1"] == "v1"
    assert report.request.body == "x=y&name=%E6%9D%B1&name=%E4%BA%AC"
    assert report.message is None

    assert isinstance(response, ResponseWrapper)
    assert response.id == "id"
    assert response.elapsed == 1.23
    assert response.status_code == 402
    assert response.headers == {"header-name": "Header-Value"}
    assert response.body.text == sentinel.text
    assert response.body.content == sentinel.content

    uuid4.assert_called()
    now.assert_called()

    # Contextual values will disappear.
    expected_context = {"foo": "bar"}
    resolve_params.assert_called_once_with(sentinel.params, expected_context)
    body.resolve.assert_called_once_with(expected_context)

    session.rebuild_proxies.assert_called_once()

    args, kwargs = session.send.call_args
    prepped = args[0]
    assert isinstance(prepped, requests.PreparedRequest)
    assert prepped.method == "POST"
    assert prepped.url == "https://a.com/path?name=%E4%BA%AC&a=b&a=c"
    assert prepped.headers["Content-Type"] == "text/plain"
    assert prepped.headers["User-Agent"].startswith("Preacher")
    assert prepped.headers["k1"] == "v1"
    assert prepped.body == "x=y&name=%E6%9D%B1&name=%E4%BA%AC"
    assert kwargs["proxies"] is sentinel.proxies
    assert kwargs["timeout"] == 5.0


def test_request_overwrites_default_headers(session, body):
    request = Request(
        headers={
            "User-Agent": "custom-user-agent",
            "Content-Type": "custom-content-type",
        },
        body=body,
    )
    requester = Requester("https://base-url.net")
    report, _res = requester.execute(request, session=session)
    assert report.request
    assert report.request.headers["User-Agent"] == "custom-user-agent"
    assert report.request.headers["Content-Type"] == "custom-content-type"
    prepped = session.send.call_args[0][0]
    assert isinstance(prepped, requests.PreparedRequest)
    assert prepped.headers["User-Agent"] == "custom-user-agent"
    assert prepped.headers["Content-Type"] == "custom-content-type"

    # Doesn't change the state.
    request = Request(body=body)
    report, _res = requester.execute(request, session=session)
    assert report.request
    assert report.request.headers["User-Agent"].startswith("Preacher")
    assert report.request.headers["Content-Type"] == "text/plain"
    prepped = session.send.call_args[0][0]
    assert isinstance(prepped, requests.PreparedRequest)
    assert prepped.headers["User-Agent"].startswith("Preacher")
    assert prepped.headers["Content-Type"] == "text/plain"
