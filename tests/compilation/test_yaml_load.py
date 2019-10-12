from io import StringIO
from unittest.mock import patch
from pytest import mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.yaml import load


@patch('builtins.open')
@mark.parametrize('content, expected_message', (
    ('!invalid foo', '!invalid'),
    ('!include []', 'string'),
    ('!include {}', 'string'),
    # ('- !include {}', ': [0]'),
    ('{key: !include {}}', ': key'),
    # ('{key: [!include {}]}', ': key[0]'),
))
def test_given_invalid_content(open_mock, content, expected_message):
    open_mock.return_value = StringIO(content)

    with raises(CompilationError) as error_info:
        load('path')
    assert expected_message in str(error_info.value)

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
