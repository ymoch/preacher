from io import StringIO
from unittest.mock import patch
from pytest import mark, raises

from preacher.compilation.error import CompilationError, IndexedNode, NamedNode
from preacher.compilation.yaml import load


@patch('builtins.open')
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
def test_given_invalid_content(
    open_mock,
    content,
    expected_message,
    expected_path,
):
    open_mock.return_value = StringIO(content)

    with raises(CompilationError) as error_info:
        load('path')
    assert expected_message in str(error_info.value)
    assert error_info.value.path == expected_path

    open_mock.assert_called_with('path')


@patch('builtins.open')
def test_given_recursive_inclusion(open_mock):
    content = '''
    list:
      - !include item.yml
      - key: !include value.yml
    recursive: !include recursive.yml
    '''
    answer_map = {
        'scenario.yml': content,
        'item.yml': 'item',
        'value.yml': 'value',
        'recursive.yml': '!include inner.yml',
        'inner.yml': 'inner',
    }
    open_mock.side_effect = lambda path: StringIO(answer_map[path])

    actual = load('scenario.yml')
    assert actual == {
        'list': [
            'item',
            {'key': 'value'},
        ],
        'recursive': 'inner',
    }


@patch('builtins.open')
def test_given_argument(open_mock):
    content = '''
    - !argument foo
    - key: !argument bar
    '''
    open_mock.return_value = StringIO(content)

    actual = load('scenario.yml')
    assert isinstance(actual, list)
    assert actual[0].key == 'foo'
    assert isinstance(actual[1], dict)
    assert actual[1]['key'].key == 'bar'
