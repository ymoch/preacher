from io import StringIO

from pytest import fixture, raises, mark

from preacher.compilation.yaml.error import YamlError
from preacher.compilation.yaml.impl.argument import ArgumentTag
from preacher.compilation.yaml.loader import Loader


@fixture
def loader() -> Loader:
    loader = Loader()
    loader.add_tag("!argument", ArgumentTag())
    return loader


@mark.parametrize(('content', 'expected_message'), [
    ('!argument []', '", line 1, column 1'),
    ('!argument {}', '", line 1, column 1'),
])
def test_given_invalid_arguments(loader: Loader, content, expected_message):
    stream = StringIO(content)
    with raises(YamlError) as error_info:
        loader.load(stream)
    assert expected_message in str(error_info.value)


def test_given_valid_arguments(loader: Loader):
    stream = StringIO('''
    - !argument foo
    - key: !argument bar
    ''')

    actual = loader.load(stream)
    assert isinstance(actual, list)
    assert actual[0].key == 'foo'
    assert isinstance(actual[1], dict)
    assert actual[1]['key'].key == 'bar'
