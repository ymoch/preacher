"""
Tests only arguments and that whole process is run.
Styles should be checked independently.
"""
import os
from concurrent.futures import (
    Executor,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)
from tempfile import TemporaryDirectory
from typing import Iterable, Optional
from unittest.mock import NonCallableMock, sentinel, call

from click.testing import CliRunner

from pytest import mark, fixture

from preacher.app.cli.main import main
from preacher.compilation.scenario import ScenarioCompiler
from preacher.core.scenario import Scenario, ScenarioRunner, Listener
from preacher.core.status import Status

PKG = 'preacher.app.cli.main'


@fixture
def base_dir():
    with TemporaryDirectory() as path:
        with open(os.path.join(path, 'foo.yml'), 'w') as f:
            f.write('foo')
        with open(os.path.join(path, 'bar.yml'), 'w') as f:
            f.write('bar')
        yield path


@mark.parametrize('args', [
    ['-h'],
    ['--help'],
    ['-v'],
    ['--version'],
])
def test_show_and_exit(args):
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0


@mark.parametrize('args', [
    ['-a', ''],
    ['--argument', 'foo'],
    ['--argument', 'foo=['],
    ['--argument', 'foo=!include file.yml'],
    ['-l', 'foo'],
    ['--level', 'bar'],
    ['-r', 'foo'],
    ['--retry', '-1'],
    ['-d', 'foo'],
    ['--delay', '-0.1'],
    ['-t', 'foo'],
    ['--timeout', '0.0'],
    ['-c', 'foo'],
    ['--concurrency', '0'],
    ['-C', 'foo'],
    ['--concurrent-executor', 'foo'],
])
def test_given_invalid_options(args):
    runner = CliRunner()
    result = runner.invoke(main, args)
    assert result.exit_code == 2


@mark.parametrize('env', [
    {},
    {
        'PREACHER_CLI_BASE_URL': '',
        'PREACHER_CLI_ARGUMENT': '',
        'PREACHER_CLI_LEVEL': '',
        'PREACHER_CLI_RETRY': '',
        'PREACHER_CLI_DELAY': '',
        'PREACHER_CLI_TIMEOUT': '',
        'PREACHER_CLI_CONCURRENCY': '',
        'PREACHER_CLI_CONCURRENT_EXECUTOR': '',
    },
])
def test_default(mocker, env):
    args = ()

    def _run_scenarios(
        executor: Executor,
        scenarios: Iterable[Scenario],
        listener: Optional[Listener] = None,
    ) -> Status:
        assert isinstance(executor, ProcessPoolExecutor)
        assert list(scenarios) == [sentinel.scenario]
        assert listener
        return Status.UNSTABLE

    runner = NonCallableMock(ScenarioRunner)
    runner.run.side_effect = _run_scenarios
    runner_ctor = mocker.patch(f'{PKG}.ScenarioRunner')
    runner_ctor.return_value = runner

    compiler = NonCallableMock(ScenarioCompiler)
    compiler.compile_flattening.return_value = [sentinel.scenario]
    compiler_ctor = mocker.patch(f'{PKG}.create_scenario_compiler')
    compiler_ctor.return_value = compiler

    result = CliRunner().invoke(main, args, input='[]', env=env)
    assert result.exit_code == 1

    compiler.compile_flattening.assert_called_once_with([], arguments={})

    runner_ctor.assert_called_once_with(
        base_url='',
        retry=0,
        delay=0.1,
        timeout=None,
    )


def test_arguments(mocker, base_dir):
    args = (
        '--base-url', 'https://your-domain.com/api',
        '-a', 'foo=',
        '--argument', 'bar=1',
        '--argument', 'baz=1.2',
        '--argument', 'spam=[ham,eggs]',
        '--level', 'unstable',
        '--retry', '5',
        '--delay', '2.5',
        '--timeout', '3.5',
        '--concurrency', '4',
        '--concurrent-executor', 'thread',
        '--report', os.path.join(base_dir, 'report/'),
        '-VV',
        os.path.join(base_dir, 'foo.yml'),
        os.path.join(base_dir, 'bar.yml'),
    )
    env = {
        'PREACHER_CLI_BASE_URL': 'https://my-domain.com/api',
        'PREACHER_CLI_ARGUMENT': 'foo',
        'PREACHER_CLI_LEVEL': 'foo',
        'PREACHER_CLI_RETRY': 'foo',
        'PREACHER_CLI_DELAY': 'foo',
        'PREACHER_CLI_TIMEOUT': 'foo',
        'PREACHER_CLI_CONCURRENCY': 'foo',
        'PREACHER_CLI_CONCURRENT_EXECUTOR': 'foo',
    }

    def _run_scenarios(
        executor: Executor,
        scenarios: Iterable[Scenario],
        listener: Optional[Listener] = None,
    ) -> Status:
        assert isinstance(executor, ThreadPoolExecutor)
        assert list(scenarios) == [sentinel.scenario] * 2
        assert listener
        return Status.SUCCESS

    runner = NonCallableMock(ScenarioRunner)
    runner.run.side_effect = _run_scenarios
    runner_ctor = mocker.patch(f'{PKG}.ScenarioRunner')
    runner_ctor.return_value = runner

    compiler = NonCallableMock(ScenarioCompiler)
    compiler.compile_flattening.return_value = [sentinel.scenario]
    compiler_ctor = mocker.patch(f'{PKG}.create_scenario_compiler')
    compiler_ctor.return_value = compiler

    result = CliRunner().invoke(main, args, env=env)
    assert result.exit_code == 0

    expected_arguments = {
        'foo': None,
        'bar': 1,
        'baz': 1.2,
        'spam': ['ham', 'eggs'],
    }
    compiler.compile_flattening.assert_has_calls([
        call('foo', arguments=expected_arguments),
        call('bar', arguments=expected_arguments),
    ])
    runner_ctor.assert_called_once_with(
        base_url='https://your-domain.com/api',
        retry=5,
        delay=2.5,
        timeout=3.5,
    )

    assert os.path.isdir(os.path.join(base_dir, 'report'))


def test_environ(mocker, base_dir):
    args = [os.path.join(base_dir, 'foo.yml')]
    env = {
        'PREACHER_CLI_BASE_URL': 'https://my-domain.com/api',
        'PREACHER_CLI_ARGUMENT': 'foo=1 spam="ham\'eggs"',
        'PREACHER_CLI_LEVEL': 'failure',
        'PREACHER_CLI_RETRY': '10',
        'PREACHER_CLI_DELAY': '1.2',
        'PREACHER_CLI_TIMEOUT': '3.4',
        'PREACHER_CLI_CONCURRENCY': '5',
        'PREACHER_CLI_CONCURRENT_EXECUTOR': 'thread',
        'PREACHER_CLI_REPORT': 'reports/',
    }

    def _run_scenarios(
        executor: Executor,
        scenarios: Iterable[Scenario],
        listener: Optional[Listener] = None,
    ) -> Status:
        assert isinstance(executor, ThreadPoolExecutor)
        assert list(scenarios) == [sentinel.scenario]
        assert listener
        return Status.SUCCESS

    runner = NonCallableMock(ScenarioRunner)
    runner.run.side_effect = _run_scenarios
    runner_ctor = mocker.patch(f'{PKG}.ScenarioRunner')
    runner_ctor.return_value = runner

    compiler = NonCallableMock(ScenarioCompiler)
    compiler.compile_flattening.return_value = [sentinel.scenario]
    compiler_ctor = mocker.patch(f'{PKG}.create_scenario_compiler')
    compiler_ctor.return_value = compiler

    result = CliRunner().invoke(main, args, env=env)
    assert result.exit_code == 0

    compiler.compile_flattening.assert_called_once_with(
        'foo',
        arguments={'foo': 1, 'spam': "ham'eggs"},
    )
    runner_ctor.assert_called_once_with(
        base_url='https://my-domain.com/api',
        retry=10,
        delay=1.2,
        timeout=3.4,
    )


def test_when_fails_unexpectedly(mocker):
    runner = NonCallableMock(ScenarioRunner)
    runner.run.side_effect = RuntimeError
    runner_ctor = mocker.patch(f'{PKG}.ScenarioRunner')
    runner_ctor.return_value = runner

    result = CliRunner().invoke(main, [], input='[]')
    assert result.exit_code == 2
