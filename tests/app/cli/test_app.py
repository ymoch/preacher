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
from unittest.mock import Mock, NonCallableMock, NonCallableMagicMock, sentinel

from pytest import fixture, raises, mark

from preacher.app.cli.app import REPORT_LOGGER_NAME
from preacher.app.cli.app import (
    app,
    create_system_logger,
    load_objs,
    create_listener,
)
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


def test_normal(mocker, base_dir, executor, executor_factory):
    logger = NonCallableMock(logging.Logger)
    logger_ctor = mocker.patch(f'{PKG}.create_system_logger')
    logger_ctor.return_value = logger

    objs_ctor = mocker.patch(f'{PKG}.load_objs')
    objs_ctor.return_value = iter([sentinel.objs])

    listener_ctor = mocker.patch(f'{PKG}.create_listener')
    listener_ctor.return_value = sentinel.listener

    compiler = NonCallableMock(ScenarioCompiler)
    compiler.compile_flattening.return_value = iter([sentinel.scenario])
    compiler_ctor = mocker.patch(f'{PKG}.create_scenario_compiler')
    compiler_ctor.return_value = compiler

    def _run(
        executor_: Executor,
        scenarios: Iterable[Scenario],
        listener: Optional[Listener],
    ) -> Status:
        assert executor_ is executor
        assert list(scenarios) == [sentinel.scenario]
        assert listener is sentinel.listener
        return Status.SUCCESS

    runner = NonCallableMock(ScenarioRunner)
    runner.run.side_effect = _run
    runner_ctor = mocker.patch(f'{PKG}.ScenarioRunner', return_value=runner)

    app(
        paths=sentinel.paths,
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

    logger_ctor.assert_called_once_with(sentinel.verbosity)
    objs_ctor.assert_called_once_with(sentinel.paths, logger)
    compiler.compile_flattening.assert_called_once_with(
        sentinel.objs,
        arguments=sentinel.args,
    )
    runner_ctor.assert_called_once_with(
        base_url=sentinel.base_url,
        retry=sentinel.retry,
        delay=sentinel.delay,
        timeout=sentinel.timeout,
    )
    listener_ctor.assert_called_once_with(sentinel.level, sentinel.report_dir)
    executor_factory.assert_called_once_with(sentinel.concurrency)
    runner.run.assert_called_once()
    executor.__exit__.assert_called_once()


def test_not_succeeds(mocker, executor_factory, executor):
    runner = NonCallableMock(ScenarioRunner)
    runner.run.return_value = Status.UNSTABLE
    mocker.patch(f'{PKG}.ScenarioRunner', return_value=runner)

    with raises(SystemExit) as error_info:
        app(executor_factory=executor_factory)
    assert error_info.value.code == 1

    executor.__exit__.assert_called_once()


def test_unexpected_error_occurs(mocker, executor_factory, executor):
    runner = NonCallableMock(ScenarioRunner)
    runner.run.side_effect = RuntimeError
    mocker.patch(f'{PKG}.ScenarioRunner', return_value=runner)

    with raises(SystemExit) as error_info:
        app(executor_factory=executor_factory)
    assert error_info.value.code == 3

    executor.__exit__.assert_called_once()


@mark.parametrize(('verbosity', 'expected_level'), [
    (0, logging.WARNING),
    (1, logging.INFO),
    (2, logging.DEBUG),
    (3, logging.DEBUG),
])
def test_create_system_logger(verbosity, expected_level):
    logger = create_system_logger(verbosity=verbosity)
    assert logger.getEffectiveLevel() == expected_level


def test_load_objs_empty(mocker):
    mocker.patch('sys.stdin', StringIO('foo\n---\nbar'))

    logger = NonCallableMock(logging.Logger)
    objs = load_objs((), logger)

    assert next(objs) == 'foo'
    assert next(objs) == 'bar'
    with raises(StopIteration):
        next(objs)


def test_load_objs_filled(base_dir):
    logger = NonCallableMock(logging.Logger)
    objs = load_objs(
        (os.path.join(base_dir, 'foo.yml'), os.path.join(base_dir, 'bar.yml')),
        logger,
    )

    assert next(objs) == 'foo'
    assert next(objs) == 'bar'
    with raises(StopIteration):
        next(objs)


@mark.parametrize(('level', 'expected_logging_level'), [
    (Status.SKIPPED, logging.DEBUG),
    (Status.SUCCESS, logging.INFO),
    (Status.UNSTABLE, logging.WARNING),
    (Status.FAILURE, logging.ERROR),
])
def test_create_listener_logging_level(level, expected_logging_level):
    create_listener(level=level, report_dir=None)

    logging_level = logging.getLogger(REPORT_LOGGER_NAME).getEffectiveLevel()
    assert logging_level == expected_logging_level


def test_create_listener_report_dir(base_dir):
    report_dir = os.path.join(base_dir, 'report')
    create_listener(level=Status.FAILURE, report_dir=report_dir)
    assert os.path.isdir(report_dir)
