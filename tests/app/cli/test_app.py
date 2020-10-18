"""
Tests only arguments and that whole process is run.
Styles should be checked independently.
"""

import logging
import os
from concurrent.futures import Executor
from io import StringIO
from tempfile import TemporaryDirectory
from typing import Iterable
from unittest.mock import Mock, NonCallableMock, NonCallableMagicMock, sentinel

from pytest import fixture, raises, mark

from preacher.app.cli.app import app
from preacher.app.cli.app import create_listener
from preacher.app.cli.app import create_scheduler
from preacher.app.cli.app import create_system_logger
from preacher.app.cli.app import load_objs
from preacher.compilation.scenario import ScenarioCompiler
from preacher.core.scenario import Scenario
from preacher.core.scheduling import ScenarioScheduler
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
def executor():
    executor = NonCallableMagicMock(Executor)
    executor.__enter__.return_value = executor
    return executor


@fixture
def executor_factory(executor):
    return Mock(return_value=executor)


def test_app_normal(mocker, base_dir, executor, executor_factory):
    logger = NonCallableMock(logging.Logger)
    logger_ctor = mocker.patch(f'{PKG}.create_system_logger', return_value=logger)

    plugin_manager_ctor = mocker.patch(f'{PKG}.get_plugin_manager')
    plugin_manager_ctor.return_value = sentinel.plugin_manager

    load_plugins_func = mocker.patch(f'{PKG}.load_plugins')

    compiler = NonCallableMock(ScenarioCompiler)
    compiler.compile_flattening.return_value = iter([sentinel.scenario])
    compiler_ctor = mocker.patch(f'{PKG}.create_scenario_compiler')
    compiler_ctor.return_value = compiler

    objs_ctor = mocker.patch(f'{PKG}.load_objs')
    objs_ctor.return_value = iter([sentinel.objs])

    listener_ctor = mocker.patch(f'{PKG}.create_listener')
    listener_ctor.return_value = sentinel.listener

    def _run(scenarios: Iterable[Scenario]) -> Status:
        assert list(scenarios) == [sentinel.scenario]
        return Status.SUCCESS

    scheduler = NonCallableMock(ScenarioScheduler)
    scheduler.run.side_effect = _run
    scheduler_ctor = mocker.patch(f'{PKG}.create_scheduler', return_value=scheduler)

    exit_code = app(
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
        plugins=sentinel.plugins,
        verbosity=sentinel.verbosity
    )
    assert exit_code == 0

    logger_ctor.assert_called_once_with(sentinel.verbosity)

    plugin_manager_ctor.assert_called_once_with()
    load_plugins_func.assert_called_once_with(sentinel.plugin_manager, sentinel.plugins, logger)

    compiler_ctor.assert_called_once_with(plugin_manager=sentinel.plugin_manager)
    compiler.compile_flattening.assert_called_once_with(sentinel.objs, arguments=sentinel.args)

    objs_ctor.assert_called_once_with(sentinel.paths, logger)
    scheduler_ctor.assert_called_once_with(
        executor=executor,
        listener=sentinel.listener,
        base_url=sentinel.base_url,
        timeout=sentinel.timeout,
        retry=sentinel.retry,
        delay=sentinel.delay,
    )
    listener_ctor.assert_called_once_with(sentinel.level, sentinel.report_dir)
    executor_factory.assert_called_once_with(sentinel.concurrency)
    scheduler.run.assert_called_once()
    executor.__exit__.assert_called_once()


def test_app_plugin_loading_fails(mocker):
    mocker.patch(f'{PKG}.load_plugins', side_effect=RuntimeError('msg'))
    assert app() == 3


def test_app_compiler_creation_fails(mocker):
    mocker.patch(f'{PKG}.create_scenario_compiler', side_effect=RuntimeError('msg'))
    assert app() == 3


def test_app_scenario_running_not_succeeds(mocker, executor_factory, executor):
    scheduler = NonCallableMock(ScenarioScheduler)
    scheduler.run.return_value = Status.UNSTABLE
    mocker.patch(f'{PKG}.ScenarioScheduler', return_value=scheduler)

    exit_code = app(executor_factory=executor_factory)
    assert exit_code == 1

    executor.__exit__.assert_called_once()


def test_app_scenario_running_raises_an_unexpected_error(mocker, executor_factory, executor):
    scheduler = NonCallableMock(ScenarioScheduler)
    scheduler.run.side_effect = RuntimeError
    mocker.patch(f'{PKG}.ScenarioScheduler', return_value=scheduler)

    exit_code = app(executor_factory=executor_factory)
    assert exit_code == 3

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

    paths = ()
    objs = load_objs(paths)

    assert next(objs) == 'foo'
    assert next(objs) == 'bar'
    with raises(StopIteration):
        next(objs)


def test_load_objs_filled(base_dir):
    paths = (os.path.join(base_dir, 'foo.yml'), os.path.join(base_dir, 'bar.yml'))
    objs = load_objs(paths)

    assert next(objs) == 'foo'
    assert next(objs) == 'bar'
    with raises(StopIteration):
        next(objs)


def test_create_scheduler(mocker):
    requester_ctor = mocker.patch(f'{PKG}.Requester', return_value=sentinel.requester)
    unit_runner_ctor = mocker.patch(f'{PKG}.UnitRunner', return_value=sentinel.unit_runner)
    case_runner_ctor = mocker.patch(f'{PKG}.CaseRunner', return_value=sentinel.case_runner)
    runner_ctor = mocker.patch(f'{PKG}.ScenarioRunner', return_value=sentinel.runner)
    scheduler_ctor = mocker.patch(f'{PKG}.ScenarioScheduler', return_value=sentinel.scheduler)

    scheduler = create_scheduler(
        executor=sentinel.executor,
        listener=sentinel.listener,
        base_url=sentinel.base_url,
        timeout=sentinel.timeout,
        retry=sentinel.retry,
        delay=sentinel.delay,
    )
    assert scheduler is sentinel.scheduler

    requester_ctor.assert_called_once_with(base_url=sentinel.base_url, timeout=sentinel.timeout)
    unit_runner_ctor.assert_called_once_with(
        requester=sentinel.requester,
        retry=sentinel.retry,
        delay=sentinel.delay,
    )
    case_runner_ctor.assert_called_once_with(unit_runner=sentinel.unit_runner)
    runner_ctor.assert_called_once_with(
        executor=sentinel.executor,
        case_runner=sentinel.case_runner,
    )
    scheduler_ctor.assert_called_once_with(runner=sentinel.runner, listener=sentinel.listener)


@mark.parametrize(('level', 'expected_logging_level'), [
    (Status.SKIPPED, logging.DEBUG),
    (Status.SUCCESS, logging.INFO),
    (Status.UNSTABLE, logging.WARNING),
    (Status.FAILURE, logging.ERROR),
])
def test_create_listener_logging_level(level, expected_logging_level):
    create_listener(level=level, report_dir=None)

    logger = logging.getLogger('preacher.cli.report.logging')
    assert logger.getEffectiveLevel() == expected_logging_level


def test_create_listener_report_dir(base_dir):
    report_dir = os.path.join(base_dir, 'report')
    create_listener(level=Status.FAILURE, report_dir=report_dir)
    assert os.path.isdir(report_dir)
