from datetime import datetime, timezone, timedelta
from io import StringIO

from pytest import mark, raises

from preacher.compilation.error import CompilationError, IndexedNode, NamedNode
from preacher.compilation.yaml import (
    PathLike,
    _Resolvable,
    load,
    load_from_path,
    load_all,
    load_all_from_path,
)
from preacher.core.interpretation import RelativeDatetime, ValueContext


def test_resolvable_interface():
    class _Incomplete(_Resolvable):
        def resolve(self, origin: PathLike) -> object:
            return super().resolve(origin)

    resolvable = _Incomplete()
    with raises(NotImplementedError):
        resolvable.resolve('')


@mark.parametrize('content, expected_message, expected_path', (
    ('!invalid foo', '!invalid', []),
    ('- !include {}', '', [IndexedNode(0)]),
    ('{key: !include {}}', '', [NamedNode('key')]),
    ('{key: [!include {}]}', '', [NamedNode('key'), IndexedNode(0)]),
))
def test_given_invalid_content(content, expected_message, expected_path):
    io = StringIO(content)
    with raises(CompilationError) as error_info:
        load(io)
    assert expected_message in str(error_info.value)
    assert error_info.value.path == expected_path


@mark.parametrize('content', [
    '!relative_datetime []',
    '!relative_datetime {}',
    '!relative_datetime invalid',
])
def test_given_invalid_relative_datetime(content):
    io = StringIO(content)
    with raises(CompilationError):
        load(io)


def test_given_valid_relative_datetime():
    io = StringIO('!relative_datetime -1 hour')
    actual = load(io)
    assert isinstance(actual, RelativeDatetime)

    now = datetime.now()
    resolved = actual.resolve(ValueContext(origin_datetime=now))
    assert resolved.value == now - timedelta(hours=1)


def test_given_valid_full_relative_datetime():
    io = StringIO('!relative_datetime {delta: -1 minute, format: "%H:%M:%S"}')
    actual = load(io)
    assert isinstance(actual, RelativeDatetime)

    now = datetime(2020, 1, 23, 12, 34, 56)
    resolved = actual.resolve(ValueContext(origin_datetime=now))
    assert resolved.formatted == '12:33:56'


def test_given_datetime_that_is_offset_naive():
    io = StringIO('2020-04-01 01:23:45')
    actual = load(io)
    assert isinstance(actual, datetime)
    assert actual == datetime(2020, 4, 1, 1, 23, 45)
    assert actual.tzinfo is None


def test_given_datetime_that_is_offset_aware():
    io = StringIO('2020-04-01 01:23:45 +09:00')
    actual = load(io)
    assert isinstance(actual, datetime)
    assert (
        actual - datetime(2020, 3, 31, 16, 23, 45, tzinfo=timezone.utc)
    ).total_seconds() == 0.0
    assert actual.tzinfo


def test_load_all_given_invalid_value():
    io = StringIO('!invalid')
    with raises(CompilationError):
        next(load_all(io))


def test_load_all_from_path(mocker):
    open_mock = mocker.patch('builtins.open')
    open_mock.return_value = StringIO('1\n---\n2\n---\n!argument foo')

    actual = load_all_from_path('path/to/foo.yaml')
    assert next(actual) == 1
    assert next(actual) == 2
    assert next(actual).key == 'foo'
    with raises(StopIteration):
        next(actual)

    open_mock.assert_called_once_with('path/to/foo.yaml')


def test_load_from_path_not_found(mocker):
    mocker.patch('builtins.open', side_effect=FileNotFoundError('message'))

    with raises(CompilationError):
        load_from_path('/////foo/bar/baz')


def test_load_all_from_path_not_found(mocker):
    mocker.patch('builtins.open', side_effect=FileNotFoundError('message'))

    objs = load_all_from_path('/////foo/bar/baz')
    with raises(CompilationError):
        next(objs)
