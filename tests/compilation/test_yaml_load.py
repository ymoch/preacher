from io import StringIO
from unittest.mock import call

from pytest import mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.yaml import (
    load,
    load_from_path,
    load_all,
    load_all_from_path,
)


@mark.parametrize(('content', 'expected_message'), (
    ('!invalid', '", line 1, column 1'),
    ('- !argument {}', '", line 1, column 3'),
    ('\nkey: !argument []\n', '", line 2, column 6'),
    ('key:\n- !argument {}', '", line 2, column 3'),
))
def test_load_given_invalid_content(content, expected_message):
    stream = StringIO(content)
    with raises(CompilationError) as error_info:
        load(stream)
    assert expected_message in str(error_info.value)


def test_load_all(mocker):
    stream = StringIO('1\n---\n!include inner/foo.yml\n---\n!x\n---\n2')
    included_content = StringIO('foo')

    open_mock = mocker.patch('builtins.open')
    open_mock.return_value = included_content

    actual = load_all(stream)
    assert next(actual) == 1
    assert next(actual) == 'foo'
    with raises(CompilationError):
        next(actual)
    with raises(StopIteration):
        next(actual)

    assert included_content.closed
    open_mock.assert_called_once_with('./inner/foo.yml')


def test_load_from_path_not_found(mocker):
    mocker.patch('builtins.open', side_effect=FileNotFoundError('message'))
    with raises(CompilationError):
        load_from_path('/////foo/bar/baz')


def test_load_from_path(mocker):
    content = StringIO('!include inner/foo.yml')
    included_content = StringIO('foo')

    open_mock = mocker.patch('builtins.open')
    open_mock.side_effect = [content, included_content]

    actual = load_from_path('path/to/scenario.yml')
    assert actual == 'foo'

    assert content.closed
    assert included_content.closed
    open_mock.assert_has_calls([
        call('path/to/scenario.yml'),
        call('path/to/inner/foo.yml'),
    ])


def test_load_all_from_path_not_found(mocker):
    mocker.patch('builtins.open', side_effect=FileNotFoundError('message'))

    objs = load_all_from_path('/////foo/bar/baz')
    with raises(CompilationError):
        next(objs)


def test_load_all_from_path(mocker):
    content = StringIO('1\n---\n!include inner/foo.yml\n---\n!x\n---\n2\n')
    included_content = StringIO('foo')

    open_mock = mocker.patch('builtins.open')
    open_mock.side_effect = [content, included_content]

    actual = load_all_from_path('path/to/scenario.yml')
    assert next(actual) == 1
    assert next(actual) == 'foo'
    with raises(CompilationError):
        next(actual)
    with raises(StopIteration):
        next(actual)

    assert content.closed
    assert included_content.closed
    open_mock.assert_has_calls([
        call('path/to/scenario.yml'),
        call('path/to/inner/foo.yml'),
    ])
