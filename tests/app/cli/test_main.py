import logging
import os
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from tempfile import TemporaryDirectory

from click.testing import CliRunner
from pytest import fixture, mark

from preacher.app.cli.main import main

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
    print(result)
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
    app = mocker.patch(f'{PKG}.app')

    result = CliRunner().invoke(main, env=env)
    assert result.exit_code == 0
    app.assert_called_once_with(
        paths=(),
        base_url='',
        arguments={},
        level=logging.INFO,
        report_dir_path=None,
        retry=0,
        delay=0.1,
        timeout=None,
        concurrency=1,
        executor_factory=ProcessPoolExecutor,
        verbosity=0,
    )


def test_arguments(mocker, base_dir):
    app = mocker.patch(f'{PKG}.app')

    args = (
        '--base-url', 'https://your-domain.com/api',
        '-a', 'foo=',
        '--argument', 'bar=1',
        '--argument', 'baz=1.2',
        '--argument', 'spam=[ham,eggs]',
        '--level', 'unstable',
        '--report', os.path.join(base_dir, 'report'),
        '--retry', '5',
        '--delay', '2.5',
        '--timeout', '3.5',
        '--concurrency', '4',
        '--executor', 'thread',
        '--verbose',
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
    result = CliRunner().invoke(main, args=args, env=env)
    assert result.exit_code == 0
    app.assert_called_once_with(
        paths=(
            os.path.join(base_dir, 'foo.yml'),
            os.path.join(base_dir, 'bar.yml'),
        ),
        base_url='https://your-domain.com/api',
        arguments={
            'foo': None,
            'bar': 1,
            'baz': 1.2,
            'spam': ['ham', 'eggs'],
        },
        level=logging.WARNING,
        report_dir_path=os.path.join(base_dir, 'report'),
        retry=5,
        delay=2.5,
        timeout=3.5,
        concurrency=4,
        executor_factory=ThreadPoolExecutor,
        verbosity=1,
    )


def test_environ(mocker):
    app = mocker.patch(f'{PKG}.app')

    env = {
        'PREACHER_CLI_BASE_URL': 'https://my-domain.com/api',
        'PREACHER_CLI_ARGUMENT': 'foo=1 bar=" baz " spam="ham\'""eggs"',
        'PREACHER_CLI_LEVEL': 'failure',
        'PREACHER_CLI_RETRY': '10',
        'PREACHER_CLI_DELAY': '1.2',
        'PREACHER_CLI_TIMEOUT': '3.4',
        'PREACHER_CLI_CONCURRENCY': '5',
        'PREACHER_CLI_CONCURRENT_EXECUTOR': 'thread',
        'PREACHER_CLI_REPORT': 'reports/',
    }
    result = CliRunner().invoke(main, env=env)
    assert result.exit_code == 0
    app.assert_called_once_with(
        paths=(),
        base_url='https://my-domain.com/api',
        arguments={'foo': 1, 'bar': 'baz', 'spam': 'ham\'eggs'},
        level=logging.ERROR,
        report_dir_path='reports/',
        retry=10,
        delay=1.2,
        timeout=3.4,
        concurrency=5,
        executor_factory=ThreadPoolExecutor,
        verbosity=0,
    )
