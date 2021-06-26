from unittest.mock import NonCallableMock, sentinel

from preacher.presentation.listener import LoggingReportingListener
from preacher.presentation.listener import create_logging_reporting_listener
from preacher.presentation.logging import LoggingReporter

PKG = "preacher.presentation.listener.logging"


def test_on_scenario():
    reporter = NonCallableMock(LoggingReporter)
    listener = LoggingReportingListener(reporter)
    listener.on_scenario(sentinel.result)
    listener.on_end(sentinel.status)

    reporter.show_scenario_result.assert_called_once_with(sentinel.result)
    reporter.show_status.assert_called_once_with(sentinel.status)


def test_create_logging_reporting_listener_given_a_reporter(mocker):
    ctor = mocker.patch(f"{PKG}.LoggingReportingListener", return_value=sentinel.listener)

    listener = create_logging_reporting_listener(reporter=sentinel.reporter)
    assert listener is sentinel.listener

    ctor.assert_called_once_with(sentinel.reporter)


def test_create_logging_reporting_listener_given_reporter_elements(mocker):
    ctor = mocker.patch(f"{PKG}.LoggingReportingListener", return_value=sentinel.listener)
    reporter_factory = mocker.patch(f'{PKG}.create_logging_reporter')
    reporter_factory.return_value = sentinel.reporter

    listener = create_logging_reporting_listener(
        logger=sentinel.logger,
        logger_name=sentinel.logger_name,
        level=sentinel.level,
        handlers=sentinel.handlers,
    )
    assert listener is sentinel.listener

    ctor.assert_called_once_with(sentinel.reporter)
    reporter_factory.assert_called_once_with(
        logger=sentinel.logger,
        logger_name=sentinel.logger_name,
        level=sentinel.level,
        handlers=sentinel.handlers,
    )
