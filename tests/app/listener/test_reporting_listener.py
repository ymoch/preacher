from unittest.mock import MagicMock, call, patch, sentinel

from preacher.app.listener.report import ReportingListener
from preacher.report.html import HtmlReporter

reporter_ctor_patch = patch('preacher.app.listener.report.HtmlReporter')


@reporter_ctor_patch
def test_given_no_item(reporter_ctor):
    reporter = MagicMock(HtmlReporter)
    reporter_ctor.return_value = reporter

    listener = ReportingListener(sentinel.path)
    listener.on_end()

    reporter_ctor.assert_called_once_with(sentinel.path)
    reporter.export_response.assert_not_called()
    reporter.export_results.assert_called_once_with([])


@reporter_ctor_patch
def test_given_items(reporter_ctor):
    reporter = MagicMock(HtmlReporter)
    reporter_ctor.return_value = reporter

    listener = ReportingListener(sentinel.path)
    listener.on_response(sentinel.response1)
    listener.on_scenario(sentinel.scenario1)
    listener.on_response(sentinel.response2)
    listener.on_response(sentinel.response3)
    listener.on_scenario(sentinel.scenario2)
    listener.on_end()

    reporter_ctor.assert_called_once_with(sentinel.path)
    reporter.export_response.assert_has_calls([
        call(sentinel.response1),
        call(sentinel.response2),
        call(sentinel.response3),
    ])
    reporter.export_results.assert_called_once_with([
        sentinel.scenario1,
        sentinel.scenario2,
    ])
