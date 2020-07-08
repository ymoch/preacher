import os
from io import StringIO

from pytest import mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.yaml import load


@mark.parametrize(('content', 'expected_message'), [
    ('!include []', 'string'),
    ('!include {}', 'string'),
])
def test_given_invalid_inclusion(content, expected_message):
    io = StringIO(content)
    with raises(CompilationError) as error_info:
        load(io)
    assert expected_message in str(error_info.value)


def test_given_recursive_inclusion(mocker):
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
    open_mock = mocker.patch('builtins.open')
    open_mock.side_effect = lambda path: StringIO(answer_map[path])

    actual = load(io, origin=os.path.join('base', 'dir'))
    assert actual == {
        'list': [
            'item',
            {'key': 'value'},
        ],
        'recursive': 'inner',
    }


def test_given_wildcard_inclusion(mocker):
    iglob_mock = mocker.patch('glob.iglob')
    iglob_mock.side_effect = (
        lambda path, recursive: iter([f'glob:{path}:{recursive}'])
    )

    io = StringIO(r'''
    'asterisk': !include '*.yml'
    'double-asterisk': !include '**.yml'
    'question': !include '?.yml'
    'parenthesis-only-opening': !include '[.yml'
    'parenthesis-only-closing': !include '].yml'
    'empty-parenthesis': !include '[].yml'
    'filled-parenthesis': !include '[abc].yml'
    ''')
    open_mock = mocker.patch('builtins.open')
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
