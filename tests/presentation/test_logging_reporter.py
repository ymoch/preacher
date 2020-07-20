import logging
from unittest.mock import NonCallableMock

from pytest import fixture

from preacher.core.status import Status
from preacher.presentation.logging import LoggingReporter
from . import FILLED_SCENARIO_RESULTS


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
