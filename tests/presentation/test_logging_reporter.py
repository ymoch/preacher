"""
Tests only that the whole process is run.
Styles should be checked independently.
"""

import logging
import sys
from unittest.mock import NonCallableMock, NonCallableMagicMock, sentinel
from uuid import uuid4

from pytest import fixture, mark

from preacher.core.status import Status
from preacher.presentation.logging import LoggingReporter, create_logging_reporter
from . import FILLED_SCENARIO_RESULTS

PKG = "preacher.presentation.logging"


@fixture
def logger():
    return NonCallableMock(logging.Logger)


@fixture
def reporter(logger):
    return LoggingReporter(logger)


def test_show_scenarios(reporter):
    for result in FILLED_SCENARIO_RESULTS:
        reporter.show_scenario_result(result)


def test_show_status(reporter):
    reporter.show_status(Status.SUCCESS)


def test_create_logging_reporter_given_a_logger(mocker):
    ctor = mocker.patch(f"{PKG}.LoggingReporter", return_value=sentinel.reporter)

    reporter = create_logging_reporter(logger=sentinel.logger)
    assert reporter is reporter

    ctor.assert_called_once_with(sentinel.logger)


@mark.parametrize(
    ("level", "expected_level"),
    (
        (Status.SKIPPED, logging.DEBUG),
        (Status.SUCCESS, logging.INFO),
        (Status.UNSTABLE, logging.WARNING),
        (Status.FAILURE, logging.ERROR),
    ),
)
def test_create_logging_reporter_given_logger_elements(mocker, level: Status, expected_level: int):
    ctor = mocker.patch(f"{PKG}.LoggingReporter", return_value=sentinel.reporter)

    logger_name = str(uuid4())
    reporter = create_logging_reporter(
        logger_name=logger_name,
        level=level,
        handlers=iter((sentinel.handler,)),
    )
    assert reporter is reporter

    logger = logging.getLogger(logger_name)
    ctor.assert_called_once_with(logger)
    assert logger.level == expected_level
    assert logger.handlers == [sentinel.handler]


def test_create_logging_reporter_given_no_parameters(mocker):
    uuid = NonCallableMagicMock(uuid4)
    uuid.__str__.return_value = __name__
    mocker.patch("uuid.uuid4", return_value=uuid)
    ctor = mocker.patch(f"{PKG}.LoggingReporter", return_value=sentinel.reporter)

    reporter = create_logging_reporter()
    assert reporter is reporter

    logger = logging.getLogger(__name__)
    ctor.assert_called_once_with(logger)
    assert logger.level == logging.INFO

    handlers = logger.handlers
    assert len(handlers) == 1
    handler = handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream is sys.stdout
    assert handler.level == logging.NOTSET
