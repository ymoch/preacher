"""
Tests only arguments and that whole process is run.
Styles should be checked independently.
"""

import logging
import os
from concurrent.futures import Executor
from tempfile import TemporaryDirectory
from typing import Iterable
from unittest.mock import NonCallableMock, NonCallableMagicMock, ANY, sentinel

from pytest import fixture

from preacher.app.cli.app import app
from preacher.app.cli.executor import ExecutorFactory
from preacher.core.scenario import Scenario
from preacher.core.scheduling import ScenarioScheduler
from preacher.core.status import Status

PKG = "preacher.app.cli.app"


@fixture
def base_dir():
    with TemporaryDirectory() as path:
        with open(os.path.join(path, "foo.yml"), "w") as f:
            f.write("foo")
        with open(os.path.join(path, "bar.yml"), "w") as f:
            f.write("bar")
        with open(os.path.join(path, "empty.yml"), "w") as f:
            f.write("[]")
        yield path


@fixture
def executor():
    executor = NonCallableMagicMock(Executor)
    executor.__enter__.return_value = executor
    return executor


@fixture
def executor_factory(executor):
    factory = NonCallableMock(ExecutorFactory)
    factory.create.return_value = executor
    return factory


def test_app_normal(mocker, base_dir, executor, executor_factory):
    logger = NonCallableMock(logging.Logger)
    logger_ctor = mocker.patch(f"{PKG}.create_system_logger", return_value=logger)

    plugin_manager_ctor = mocker.patch(f"{PKG}.get_plugin_manager")
    plugin_manager_ctor.return_value = sentinel.plugin_manager

    load_plugins_func = mocker.patch(f"{PKG}.load_plugins")

    load_from_paths = mocker.patch(f"{PKG}.load_from_paths", return_value=sentinel.objs)
    compile_scenarios = mocker.patch(f"{PKG}.compile_scenarios")
    compile_scenarios.return_value = iter([sentinel.scenario])

    listener_ctor = mocker.patch(f"{PKG}.create_listener")
    listener_ctor.return_value = sentinel.listener

    def _run(scenarios: Iterable[Scenario]) -> Status:
        assert list(scenarios) == [sentinel.scenario]
        return Status.SUCCESS

    scheduler = NonCallableMock(ScenarioScheduler)
    scheduler.run.side_effect = _run
    scheduler_ctor = mocker.patch(f"{PKG}.create_scheduler", return_value=scheduler)

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
        verbosity=sentinel.verbosity,
    )
    assert exit_code == 0

    logger_ctor.assert_called_once_with(sentinel.verbosity)

    plugin_manager_ctor.assert_called_once_with()
    load_plugins_func.assert_called_once_with(sentinel.plugin_manager, sentinel.plugins, logger)

    load_from_paths.assert_called_once_with(
        sentinel.paths,
        plugin_manager=sentinel.plugin_manager,
        logger=logger,
    )
    compile_scenarios.assert_called_once_with(
        sentinel.objs,
        arguments=sentinel.args,
        plugin_manager=sentinel.plugin_manager,
        logger=logger,
    )
    listener_ctor.assert_called_once_with(
        level=sentinel.level,
        formatter=ANY,
        report_dir=sentinel.report_dir,
    )
    scheduler_ctor.assert_called_once_with(
        executor=executor,
        listener=sentinel.listener,
        base_url=sentinel.base_url,
        timeout=sentinel.timeout,
        retry=sentinel.retry,
        delay=sentinel.delay,
    )
    executor_factory.create.assert_called_once_with(sentinel.concurrency)
    scheduler.run.assert_called_once()
    executor.__exit__.assert_called_once()


def test_app_plugin_loading_fails(mocker):
    mocker.patch(f"{PKG}.load_plugins", side_effect=RuntimeError("msg"))
    assert app() == 3


def test_app_scenario_running_not_succeeds(mocker, executor_factory, executor):
    scheduler = NonCallableMock(ScenarioScheduler)
    scheduler.run.return_value = Status.UNSTABLE
    mocker.patch(f"{PKG}.create_scheduler", return_value=scheduler)

    exit_code = app(executor_factory=executor_factory)
    assert exit_code == 1

    executor.__exit__.assert_called_once()


def test_app_scenario_running_raises_an_unexpected_error(mocker, executor_factory, executor):
    scheduler = NonCallableMock(ScenarioScheduler)
    scheduler.run.side_effect = RuntimeError
    mocker.patch(f"{PKG}.create_scheduler", return_value=scheduler)

    exit_code = app(executor_factory=executor_factory)
    assert exit_code == 3

    executor.__exit__.assert_called_once()
