import logging

from pytest import mark, raises

from preacher.app.cli.option import parse_args


@mark.parametrize('argv', [
    ['-h'],
    ['--help'],
    ['-v'],
    ['--version'],
])
def test_show_and_exit(argv):
    with raises(SystemExit) as ex_info:
        parse_args(argv=argv)
    assert ex_info.value.code == 0


@mark.parametrize('argv', [
    [],
    ['scenario.yml', '-a', ''],
    ['scenario.yml', '--argument', 'foo'],
    ['scenario.yml', '--argument', 'foo=['],
    ['scenario.yml', '--argument', 'foo=!include file.yml'],
    ['-l', 'foo', 'scenario.yml'],
    ['--level', 'bar', 'scenario.yml'],
    ['-r', 'foo', 'scenario.yml'],
    ['--retry', '-1', 'scenario.yml'],
    ['-d', 'foo', 'scenario.yml'],
    ['--delay', '-0.1', 'scenario.yml'],
    ['-t', 'foo', 'scenario.yml'],
    ['--timeout', '0.0', 'scenario.yml'],
    ['-c', 'foo', 'scenario.yml'],
    ['--concurrency', '0', 'scenario.yml'],
])
def test_invalid_argv(argv):
    with raises(SystemExit) as ex_info:
        parse_args(argv=argv)
    assert ex_info.value.code == 2


@mark.parametrize('environ', [
    {'PREACHER_CLI_ARGUMENT': '"'},
])
def test_invalid_argument_environ(environ):
    with raises(RuntimeError) as error_info:
        parse_args(argv=['foo.yml'], environ=environ)
    assert str(error_info.value).startswith(
        'Failed to parse PREACHER_CLI_ARGUMENT:'
    )


@mark.parametrize('environ', [
    {'PREACHER_CLI_LEVEL': 'foo'},
    {'PREACHER_CLI_RETRY': 'foo'},
    {'PREACHER_CLI_DELAY': 'foo'},
    {'PREACHER_CLI_TIMEOUT': 'foo'},
    {'PREACHER_CLI_CONCURRENCY': 'foo'},
])
def test_invalid_environ(environ):
    with raises(SystemExit) as ex_info:
        parse_args(argv=['foo.yml'], environ=environ)
    assert ex_info.value.code == 2


@mark.parametrize('environ', [
    None,
    {},
    {
        'PREACHER_CLI_BASE_URL': '',
        'PREACHER_CLI_ARGUMENT': '',
        'PREACHER_CLI_LEVEL': '',
        'PREACHER_CLI_RETRY': '',
        'PREACHER_CLI_DELAY': '',
        'PREACHER_CLI_TIMEOUT': '',
        'PREACHER_CLI_CONCURRENCY': '',
    },
])
def test_default(environ):
    args = parse_args(argv=['scenario.yml'], environ=environ)
    assert args.url == ''
    assert args.argument == {}
    assert args.level == logging.INFO
    assert args.retry == 0
    assert args.delay == 0.1
    assert args.timeout is None
    assert args.concurrency == 1
    assert args.report is None
    assert args.scenario == ['scenario.yml']


def test_valid_argv():
    args = parse_args(
        argv=[
            '--url', 'https://your-domain.com/api',
            '--argument', 'foo=', 'bar=1', 'baz=1.2', 'spam=[ham,eggs]',
            '--level', 'unstable',
            '--retry', '5',
            '--delay', '2.5',
            '--timeout', '3.5',
            '--concurrency', '4',
            '--report', 'report/',
            'scenario1.yml', 'scenario2.yml',
        ],
        environ={
            'PREACHER_CLI_BASE_URL': 'https://my-domain.com/api',
            'PREACHER_CLI_ARGUMENT': 'foo',
            'PREACHER_CLI_LEVEL': 'foo',
            'PREACHER_CLI_RETRY': 'foo',
            'PREACHER_CLI_DELAY': 'foo',
            'PREACHER_CLI_TIMEOUT': 'foo',
            'PREACHER_CLI_CONCURRENCY': 'foo',
        },
    )
    assert args.url == 'https://your-domain.com/api'
    assert args.argument == {
        'foo': None,
        'bar': 1,
        'baz': 1.2,
        'spam': ['ham', 'eggs'],
    }
    assert args.level == logging.WARNING
    assert args.retry == 5
    assert args.delay == 2.5
    assert args.timeout == 3.5
    assert args.concurrency == 4
    assert args.report == 'report/'
    assert args.scenario == ['scenario1.yml', 'scenario2.yml']


def test_valid_environ():
    args = parse_args(
        argv=['scenario.yml'],
        environ={
            'PREACHER_CLI_BASE_URL': 'https://my-domain.com/api',
            'PREACHER_CLI_ARGUMENT': 'foo=1 spam="ham""\'eggs"',
            'PREACHER_CLI_LEVEL': 'failure',
            'PREACHER_CLI_RETRY': '10',
            'PREACHER_CLI_DELAY': '1.2',
            'PREACHER_CLI_TIMEOUT': '3.4',
            'PREACHER_CLI_CONCURRENCY': '5',
            'PREACHER_CLI_REPORT': 'reports/',
        },
    )
    assert args.url == 'https://my-domain.com/api'
    assert args.argument == {'foo': 1, 'spam': "ham'eggs"}
    assert args.level == logging.ERROR
    assert args.retry == 10
    assert args.delay == 1.2
    assert args.timeout == 3.4
    assert args.concurrency == 5
    assert args.report == 'reports/'
    assert args.scenario == ['scenario.yml']
