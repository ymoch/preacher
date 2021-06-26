from unittest.mock import NonCallableMock, patch, sentinel

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


@patch(f"{PKG}.LoggingReportingListener", return_value=sentinel.listener)
@patch(f"{PKG}.LoggingReporter", return_value=sentinel.logger)
def test_from_logger(logger_ctor, listener_ctor):
    listener = LoggingReportingListener.from_logger(sentinel.py_logger)
    assert listener is sentinel.listener

    logger_ctor.assert_called_once_with(sentinel.py_logger)
    listener_ctor.assert_called_once_with(sentinel.logger)
