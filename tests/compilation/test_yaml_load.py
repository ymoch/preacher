import os
from datetime import datetime, timezone, timedelta
from io import StringIO
from unittest.mock import patch

from pytest import mark, raises

from preacher.compilation.error import CompilationError, IndexedNode, NamedNode
from preacher.compilation.yaml import load, load_all, load_all_from_path
from preacher.core.interpretation.value import RelativeDatetimeValue


@mark.parametrize('content, expected_message, expected_path', (
    ('!invalid foo', '!invalid', []),
    ('!include []', 'string', []),
    ('!argument []', 'string', []),
    ('!include {}', 'string', []),
    ('!argument {}', 'string', []),
    ('- !include {}', '', [IndexedNode(0)]),
    ('- !argument {}', '', [IndexedNode(0)]),
    ('{key: !include {}}', '', [NamedNode('key')]),
    ('{key: !argument {}}', '', [NamedNode('key')]),
    ('{key: [!include {}]}', '', [NamedNode('key'), IndexedNode(0)]),
    ('{key: [!argument {}]}', '', [NamedNode('key'), IndexedNode(0)]),
))
def test_given_invalid_content(content, expected_message, expected_path):
    io = StringIO(content)
    with raises(CompilationError) as error_info:
        load(io)
    assert expected_message in str(error_info.value)
    assert error_info.value.path == expected_path


@patch('builtins.open')
def test_given_recursive_inclusion(open_mock):
    io = StringIO('''
    list:
      - !include item.yml
      - key: !include value.yml
    recursive: !include recursive.yml
    ''')
    answer_map = {
        os.path.join('base', 'dir', 'item.yml'): 'item',
        os.path.join('base', 'dir', 'value.yml'): 'value',
        os.path.join('base', 'dir', 'recursive.yml'): '!include inner.yml',
        os.path.join('base', 'dir', 'inner.yml'): 'inner',
    }
    open_mock.side_effect = lambda path: StringIO(answer_map[path])
    actual = load(io, origin=os.path.join('base', 'dir'))
    assert actual == {
        'list': [
            'item',
            {'key': 'value'},
        ],
        'recursive': 'inner',
    }


@patch('builtins.open')
@patch('glob.iglob')
def test_given_wildcard_inclusion(iglob_mock, open_mock):
    io = StringIO(r'''
    'asterisk': !include '*.yml'
    'double-asterisk': !include '**.yml'
    'question': !include '?.yml'
    'parenthesis-only-opening': !include '[.yml'
    'parenthesis-only-closing': !include '].yml'
    'empty-parenthesis': !include '[].yml'
    'filled-parenthesis': !include '[abc].yml'
    ''')
    iglob_mock.side_effect = (
        lambda path, recursive: iter([f'glob:{path}:{recursive}'])
    )
    open_mock.side_effect = lambda path: StringIO(path)

    actual = load(io, origin='base/path/')
    assert isinstance(actual, dict)
    assert actual['asterisk'] == ['glob:base/path/*.yml:True']
    assert actual['double-asterisk'] == ['glob:base/path/**.yml:True']
    assert actual['question'] == ['glob:base/path/?.yml:True']
    assert actual['parenthesis-only-closing'] == 'base/path/].yml'
    assert actual['parenthesis-only-opening'] == 'base/path/[.yml'
    assert actual['empty-parenthesis'] == 'base/path/[].yml'
    assert actual['filled-parenthesis'] == ['glob:base/path/[abc].yml:True']


def test_given_argument():
    io = StringIO('''
    - !argument foo
    - key: !argument bar
    ''')

    actual = load(io)
    assert isinstance(actual, list)
    assert actual[0].key == 'foo'
    assert isinstance(actual[1], dict)
    assert actual[1]['key'].key == 'bar'


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
    assert isinstance(actual, RelativeDatetimeValue)

    now = datetime.now()
    assert (
        actual.apply_context(origin_datetime=now)
        == now - timedelta(hours=1)
    )


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


@patch('builtins.open')
def test_load_all_from_path(open_mock):
    io = StringIO('1\n---\n2\n---\n!argument foo')
    open_mock.return_value = io
    actual = load_all_from_path('path/to/foo.yaml')
    assert next(actual) == 1
    assert next(actual) == 2
    assert next(actual).key == 'foo'
    with raises(StopIteration):
        next(actual)

    open_mock.assert_called_once_with('path/to/foo.yaml')
