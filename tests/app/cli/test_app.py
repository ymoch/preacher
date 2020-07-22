"""
Tests only arguments and that whole process is run.
Styles should be checked independently.
"""
import logging
import os
from concurrent.futures import Executor
from io import StringIO
from tempfile import TemporaryDirectory
from typing import Iterable, Optional
from unittest.mock import (
    Mock,
    NonCallableMock,
    NonCallableMagicMock,
    call,
    sentinel,
)

from pytest import fixture, raises, mark

from preacher.app.cli.app import REPORT_LOGGER_NAME
from preacher.app.cli.app import app, create_system_logger, create_listener
from preacher.compilation.scenario import ScenarioCompiler
from preacher.core.scenario import Scenario, ScenarioRunner, Listener
from preacher.core.status import Status

PKG = 'preacher.app.cli.app'


@fixture
def base_dir():
    with TemporaryDirectory() as path:
        with open(os.path.join(path, 'foo.yml'), 'w') as f:
            f.write('foo')
        with open(os.path.join(path, 'bar.yml'), 'w') as f:
            f.write('bar')
        with open(os.path.join(path, 'empty.yml'), 'w') as f:
            f.write('[]')
        yield path


@fixture
def compiler():
    compiler = NonCallableMock(ScenarioCompiler)
    compiler.compile_flattening.return_value = [sentinel.scenario]
    return compiler


@fixture
def executor():
    executor = NonCallableMagicMock(Executor)
    executor.__enter__.return_value = executor
    return executor


@fixture
def executor_factory(executor):
    return Mock(return_value=executor)


def test_normal(mocker, base_dir, compiler, executor, executor_factory):
    logger_ctor = mocker.patch(f'{PKG}.create_system_logger')
    logger_ctor.return_value = NonCallableMock(logging.Logger)

    listener_ctor = mocker.patch(f'{PKG}.create_listener')
    listener_ctor.return_value = sentinel.listener

    compiler_ctor = mocker.patch(f'{PKG}.create_scenario_compiler')
    compiler_ctor.return_value = compiler

    def _run_scenarios(
        xtor: Executor,
        scenarios: Iterable[Scenario],
        listener: Optional[Listener] = None,
    ) -> Status:
        assert xtor is executor
        assert list(scenarios) == [sentinel.scenario] * 2
        assert listener is sentinel.listener
        return Status.SUCCESS

    runner = NonCallableMock(ScenarioRunner)
    runner.run.side_effect = _run_scenarios
    runner_ctor = mocker.patch(f'{PKG}.ScenarioRunner', return_value=runner)

    app(
        paths=(
            os.path.join(base_dir, 'foo.yml'),
            os.path.join(base_dir, 'bar.yml'),
        ),
        base_url=sentinel.base_url,
        arguments=sentinel.args,
        level=sentinel.level,
        report_dir=sentinel.report_dir,
        retry=sentinel.retry,
        delay=sentinel.delay,
        timeout=sentinel.timeout,
        concurrency=sentinel.concurrency,
        executor_factory=executor_factory,
        verbosity=sentinel.verbosity
    )

    executor.__exit__.assert_called_once()
    compiler.compile_flattening.assert_has_calls([
        call('foo', arguments=sentinel.args),
        call('bar', arguments=sentinel.args),
    ])

    logger_ctor.assert_called_once_with(sentinel.verbosity)
    runner_ctor.assert_called_once_with(
        base_url=sentinel.base_url,
        retry=sentinel.retry,
        delay=sentinel.delay,
        timeout=sentinel.timeout,
    )
    listener_ctor.assert_called_once_with(sentinel.level, sentinel.report_dir)


def test_simple(mocker, base_dir, compiler):
    mocker.patch('sys.stdin', StringIO('baz'))

    compiler_ctor = mocker.patch(f'{PKG}.create_scenario_compiler')
    compiler_ctor.return_value = compiler

    def _run_scenarios(
        executor: Executor,
        scenarios: Iterable[Scenario],
        listener: Optional[Listener] = None,
    ) -> Status:
        assert list(scenarios) == [sentinel.scenario]
        return Status.SUCCESS

    runner = NonCallableMock(ScenarioRunner)
    runner.run.side_effect = _run_scenarios
    mocker.patch(f'{PKG}.ScenarioRunner', return_value=runner)

    app()

    compiler.compile_flattening.assert_called_once_with('baz', arguments={})
    runner.run.assert_called()


def test_not_succeeds(mocker, base_dir, executor_factory):
    runner = NonCallableMock(ScenarioRunner)
    runner.run.return_value = Status.UNSTABLE
    mocker.patch(f'{PKG}.ScenarioRunner', return_value=runner)

    with raises(SystemExit) as error_info:
        app(paths=(os.path.join(base_dir, 'empty.yml'),))
    assert error_info.value.code == 1


def test_unexpected_error_occurs(mocker, base_dir):
    runner = NonCallableMock(ScenarioRunner)
    runner.run.side_effect = RuntimeError
    mocker.patch(f'{PKG}.ScenarioRunner', return_value=runner)

    with raises(SystemExit) as error_info:
        app(paths=(os.path.join(base_dir, 'empty.yml'),))
    assert error_info.value.code == 3


@mark.parametrize(('verbosity', 'expected_level'), [
    (0, logging.WARNING),
    (1, logging.INFO),
    (2, logging.DEBUG),
    (3, logging.DEBUG),
])
def test_create_system_logger(verbosity, expected_level):
    logger = create_system_logger(verbosity=verbosity)
    assert logger.getEffectiveLevel() == expected_level


@mark.parametrize(('level', 'expected_logging_level'), [
    (Status.SKIPPED, logging.DEBUG),
    (Status.SUCCESS, logging.INFO),
    (Status.UNSTABLE, logging.WARNING),
    (Status.FAILURE, logging.ERROR),
])
def test_create_listener_logging_level(level, expected_logging_level):
    create_listener(level=level)

    logging_level = logging.getLogger(REPORT_LOGGER_NAME).getEffectiveLevel()
    assert logging_level == expected_logging_level


def test_create_listener_report_dir(base_dir):
    report_dir = os.path.join(base_dir, 'report')
    create_listener(report_dir=report_dir)
    assert os.path.isdir(report_dir)
