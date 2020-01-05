import logging
from unittest.mock import MagicMock, call

from pytest import fixture

from preacher.app.listener.logging import LoggingListener
from preacher.core.scenario import ScenarioResult
from preacher.core.status import Status


@fixture
def listener(logger):
    return LoggingListener(logger)


@fixture
def logger():
    return MagicMock(logging.Logger)


def test_given_empty_scenario(listener, logger):
    listener.on_scenario(ScenarioResult())
    logger.log.assert_has_calls([
        call(logging.DEBUG, '%s: %s', 'Not labeled scenario', Status.SKIPPED),
        call(logging.DEBUG, ''),
    ])
