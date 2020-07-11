from io import StringIO

from pytest import raises, mark

from preacher.compilation.error import CompilationError
from preacher.compilation.yaml import load


@mark.parametrize(('content', 'expected_message'), [
    ('!argument []', '", line 1, column 1'),
    ('!argument {}', '", line 1, column 1'),
])
def test_given_invalid_arguments(content, expected_message):
    stream = StringIO(content)
    with raises(CompilationError) as error_info:
        load(stream)
    assert expected_message in str(error_info.value)


def test_given_valid_arguments():
    stream = StringIO('''
    - !argument foo
    - key: !argument bar
    ''')

    actual = load(stream)
    assert isinstance(actual, list)
    assert actual[0].key == 'foo'
    assert isinstance(actual[1], dict)
    assert actual[1]['key'].key == 'bar'
