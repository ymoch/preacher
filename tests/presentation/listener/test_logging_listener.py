from unittest.mock import MagicMock, patch, sentinel

from preacher.presentation.listener import LoggingListener
from preacher.presentation.log import Logger

PACKAGE = 'preacher.presentation.listener.log'


def test_on_scenario():
    reporter = MagicMock(Logger)
    listener = LoggingListener(reporter)
    listener.on_scenario(sentinel.result)
    listener.on_end(sentinel.status)

    reporter.show_scenario_result.assert_called_once_with(sentinel.result)
    reporter.show_status.assert_called_once_with(sentinel.status)


@patch(f'{PACKAGE}.LoggingListener', return_value=sentinel.listener)
@patch(f'{PACKAGE}.Logger', return_value=sentinel.logger)
def test_from_logger(logger_ctor, listener_ctor):
    listener = LoggingListener.from_logger(sentinel.py_logger)
    assert listener is sentinel.listener

    logger_ctor.assert_called_once_with(sentinel.py_logger)
    listener_ctor.assert_called_once_with(sentinel.logger)
