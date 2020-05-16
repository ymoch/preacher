import os
from datetime import datetime, timezone
from io import StringIO
from unittest.mock import patch

from pytest import mark, raises

from preacher.compilation.error import CompilationError, IndexedNode, NamedNode
from preacher.compilation.yaml import load


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
        os.path.join('base/dir', 'item.yml'): 'item',
        os.path.join('base/dir', 'value.yml'): 'value',
        os.path.join('base/dir', 'recursive.yml'): '!include inner.yml',
        os.path.join('base/dir', 'inner.yml'): 'inner',
    }
    open_mock.side_effect = lambda path: StringIO(answer_map[path])
    actual = load(io, 'base/dir/')
    assert actual == {
        'list': [
            'item',
            {'key': 'value'},
        ],
        'recursive': 'inner',
    }


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


def test_given_datetime():
    io = StringIO('2020-04-01 01:23:45 +09:00')
    actual = load(io)
    assert isinstance(actual, datetime)
    assert (
        actual - datetime(2020, 3, 31, 16, 23, 45, tzinfo=timezone.utc)
    ).total_seconds() == 0.0
    assert actual.tzinfo == timezone.utc
