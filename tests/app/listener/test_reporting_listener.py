from unittest.mock import MagicMock, call, patch, sentinel

from pytest import fixture

from preacher.app.listener import ReportingListener
from preacher.app.presentation.report import Reporter

PACKAGE = 'preacher.app.listener.report'


@fixture
def reporter():
    return MagicMock(Reporter)


def test_given_no_item(reporter):
    listener = ReportingListener(reporter)
    listener.on_end()

    reporter.export_response.assert_not_called()
    reporter.export_results.assert_called_once_with([])


def test_given_items(reporter):
    listener = ReportingListener(reporter)
    listener.on_response(sentinel.response1)
    listener.on_scenario(sentinel.scenario1)
    listener.on_response(sentinel.response2)
    listener.on_response(sentinel.response3)
    listener.on_scenario(sentinel.scenario2)
    listener.on_end()

    reporter.export_response.assert_has_calls([
        call(sentinel.response1),
        call(sentinel.response2),
        call(sentinel.response3),
    ])
    reporter.export_results.assert_called_once_with([
        sentinel.scenario1,
        sentinel.scenario2,
    ])


@patch(f'{PACKAGE}.ReportingListener', return_value=sentinel.listener)
@patch(f'{PACKAGE}.Reporter', return_value=sentinel.reporter)
def test_from_logger(reporter_ctor, listener_ctor):
    listener = ReportingListener.from_path(sentinel.path)
    assert listener is sentinel.listener

    reporter_ctor.assert_called_once_with(sentinel.path)
    listener_ctor.assert_called_once_with(sentinel.reporter)
