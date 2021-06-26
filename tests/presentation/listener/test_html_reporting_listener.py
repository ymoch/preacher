from unittest.mock import NonCallableMock, call, patch, sentinel

from pytest import fixture

from preacher.presentation.html import HtmlReporter
from preacher.presentation.listener import HtmlReportingListener

PKG = "preacher.presentation.listener.html"


@fixture
def reporter():
    return NonCallableMock(HtmlReporter)


def test_given_no_item(reporter):
    listener = HtmlReportingListener(reporter)
    listener.on_end(sentinel.status)

    reporter.export_response.assert_not_called()
    reporter.export_results.assert_called_once_with([])


def test_given_items(reporter):
    listener = HtmlReportingListener(reporter)
    listener.on_execution(sentinel.execution1, sentinel.response1)
    listener.on_scenario(sentinel.scenario1)
    listener.on_execution(sentinel.execution2, sentinel.response2)
    listener.on_execution(sentinel.execution_none, None)
    listener.on_execution(sentinel.execution3, sentinel.response3)
    listener.on_scenario(sentinel.scenario2)
    listener.on_end(sentinel.status)

    reporter.export_response.assert_has_calls(
        [
            call(sentinel.execution1, sentinel.response1),
            call(sentinel.execution2, sentinel.response2),
            call(sentinel.execution3, sentinel.response3),
        ]
    )
    reporter.export_results.assert_called_once_with(
        [
            sentinel.scenario1,
            sentinel.scenario2,
        ]
    )


@patch(f"{PKG}.HtmlReportingListener", return_value=sentinel.listener)
@patch(f"{PKG}.HtmlReporter", return_value=sentinel.reporter)
def test_from_path(reporter_ctor, listener_ctor):
    listener = HtmlReportingListener.from_path(sentinel.path)
    assert listener is sentinel.listener

    reporter_ctor.assert_called_once_with(sentinel.path)
    listener_ctor.assert_called_once_with(sentinel.reporter)
