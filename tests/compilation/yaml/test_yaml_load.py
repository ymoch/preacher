import os
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import call

from pytest import fixture, mark, raises

from preacher.compilation.yaml.error import YamlError
from preacher.compilation.yaml.impl import add_default_tags
from preacher.compilation.yaml.integration import load_from_paths
from preacher.compilation.yaml.loader import Loader


@fixture
def loader() -> Loader:
    loader = Loader()
    add_default_tags(loader)
    return loader


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


@mark.parametrize(('content', 'expected_message'), (
    ('!invalid', '", line 1, column 1'),
    ('- !argument {}', '", line 1, column 3'),
    ('\nkey: !argument []\n', '", line 2, column 6'),
    ('key:\n- !argument {}', '", line 2, column 3'),
))
def test_load_given_invalid_content(loader, content, expected_message):
    stream = StringIO(content)
    with raises(YamlError) as error_info:
        loader.load(stream)
    assert expected_message in str(error_info.value)


def test_load_all(mocker, loader):
    stream = StringIO('1\n---\n!include inner/foo.yml\n---\n!x\n---\n2')
    included_content = StringIO('foo')

    open_mock = mocker.patch('builtins.open')
    open_mock.return_value = included_content

    actual = loader.load_all(stream)
    assert next(actual) == 1
    assert next(actual) == 'foo'
    with raises(YamlError):
        next(actual)
    with raises(StopIteration):
        next(actual)

    assert included_content.closed
    open_mock.assert_called_once_with('./inner/foo.yml')


def test_load_from_path_not_found(mocker, loader):
    mocker.patch('builtins.open', side_effect=FileNotFoundError('message'))
    with raises(YamlError):
        loader.load_from_path('/////foo/bar/baz')


def test_load_from_path(mocker, loader):
    content = StringIO('!include inner/foo.yml')
    included_content = StringIO('foo')

    open_mock = mocker.patch('builtins.open')
    open_mock.side_effect = [content, included_content]

    actual = loader.load_from_path('path/to/scenario.yml')
    assert actual == 'foo'

    assert content.closed
    assert included_content.closed
    open_mock.assert_has_calls([call('path/to/scenario.yml'), call('path/to/inner/foo.yml')])


def test_load_all_from_path_not_found(mocker, loader):
    mocker.patch('builtins.open', side_effect=FileNotFoundError('message'))

    objs = loader.load_all_from_path('/////foo/bar/baz')
    with raises(YamlError):
        next(objs)


def test_load_all_from_path(mocker, loader):
    content = StringIO('1\n---\n!include inner/foo.yml\n---\n!x\n---\n2\n')
    included_content = StringIO('foo')

    open_mock = mocker.patch('builtins.open')
    open_mock.side_effect = [content, included_content]

    actual = loader.load_all_from_path('path/to/scenario.yml')
    assert next(actual) == 1
    assert next(actual) == 'foo'
    with raises(YamlError):
        next(actual)
    with raises(StopIteration):
        next(actual)

    assert content.closed
    assert included_content.closed
    open_mock.assert_has_calls([call('path/to/scenario.yml'), call('path/to/inner/foo.yml')])


def test_load_objs_empty(mocker):
    mocker.patch('sys.stdin', StringIO('foo\n---\nbar'))

    paths = ()
    objs = load_from_paths(paths)

    assert next(objs) == 'foo'
    assert next(objs) == 'bar'
    with raises(StopIteration):
        next(objs)


def test_load_objs_filled(base_dir):
    paths = (os.path.join(base_dir, 'foo.yml'), os.path.join(base_dir, 'bar.yml'))
    objs = load_from_paths(paths)

    assert next(objs) == 'foo'
    assert next(objs) == 'bar'
    with raises(StopIteration):
        next(objs)
