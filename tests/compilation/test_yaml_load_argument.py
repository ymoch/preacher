from io import StringIO

from pytest import raises, mark

from preacher.compilation.error import CompilationError
from preacher.compilation.yaml import load


@mark.parametrize(('content', 'expected_message'), [
    ('!argument []', 'string'),
    ('!argument {}', 'string'),
])
def test_given_invalid_arguments(content, expected_message):
    io = StringIO(content)
    with raises(CompilationError) as error_info:
        load(io)
    assert expected_message in str(error_info.value)


def test_given_valid_arguments():
    io = StringIO('''
    - !argument foo
    - key: !argument bar
    ''')

    actual = load(io)
    assert isinstance(actual, list)
    assert actual[0].key == 'foo'
    assert isinstance(actual[1], dict)
    assert actual[1]['key'].key == 'bar'
