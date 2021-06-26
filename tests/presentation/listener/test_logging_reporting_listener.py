from unittest.mock import NonCallableMock, sentinel

from preacher.presentation.listener import LoggingReportingListener
from preacher.presentation.logging import LoggingReporter

PKG = "preacher.presentation.listener.logging"


def test_on_scenario():
    reporter = NonCallableMock(LoggingReporter)
    listener = LoggingReportingListener(reporter)
    listener.on_scenario(sentinel.result)
    listener.on_end(sentinel.status)

    reporter.show_scenario_result.assert_called_once_with(sentinel.result)
    reporter.show_status.assert_called_once_with(sentinel.status)
