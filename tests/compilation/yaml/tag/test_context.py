from io import StringIO

from pytest import fixture, mark, raises
from yamlen import Loader, YamlenError

from preacher.compilation.yaml.tag.context import ContextTag
from preacher.core.value.impl.context import ContextualValue


@fixture
def loader() -> Loader:
    loader = Loader()
    loader.add_tag("!context", ContextTag())
    return loader


@mark.parametrize(
    ("content", "expected_message"),
    (("!context []", '", line 1, column 1'), ("!context {}", '", line 1, column 1')),
)
def test_given_invalid_arguments(loader: Loader, content, expected_message):
    stream = StringIO(content)
    with raises(YamlenError) as error_info:
        loader.load(stream)
    assert expected_message in str(error_info.value)


def test_given_valid_arguments(loader: Loader):
    stream = StringIO("!context key")
    actual = loader.load(stream)
    assert isinstance(actual, ContextualValue)
    assert actual.key == "key"
