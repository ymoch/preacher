from unittest.mock import MagicMock, patch, sentinel

from preacher.app.listener.log import LoggingListener
from preacher.report.log import LoggingReporter

PACKAGE = 'preacher.app.listener.log'


def test_on_scenario():
    reporter = MagicMock(LoggingReporter)
    listener = LoggingListener(reporter)
    listener.on_scenario(sentinel.result)

    reporter.show_scenario_result.assert_called_once_with(sentinel.result)


@patch(f'{PACKAGE}.LoggingListener', return_value=sentinel.listener)
@patch(f'{PACKAGE}.LoggingReporter', return_value=sentinel.reporter)
def test_from_logger(reporter_ctor, listener_ctor):
    listener = LoggingListener.from_logger(sentinel.logger)
    assert listener is sentinel.listener

    reporter_ctor.assert_called_once_with(sentinel.logger)
    listener_ctor.assert_called_once_with(sentinel.reporter)
