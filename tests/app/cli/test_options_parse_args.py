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


def test_default_args():
    args = parse_args(['scenario.yml'])
    assert args.level == logging.INFO
    assert args.retry == 0
    assert args.delay == 0.1
    assert args.timeout is None
    assert args.concurrency == 1
    assert args.report is None
    assert args.scenario == ['scenario.yml']


def test_valid_args():
    args = parse_args([
        '--url', 'https://your-domain.com/api',
        '--level', 'unstable',
        '--retry', '5',
        '--delay', '2.5',
        '--timeout', '3.5',
        '--concurrency', '4',
        '--report', 'report/',
        'scenario1.yml', 'scenario2.yml',
    ])
    assert args.url == 'https://your-domain.com/api'
    assert args.level == logging.WARNING
    assert args.retry == 5
    assert args.delay == 2.5
    assert args.timeout == 3.5
    assert args.concurrency == 4
    assert args.report == 'report/'
    assert args.scenario == ['scenario1.yml', 'scenario2.yml']
