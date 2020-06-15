from unittest.mock import MagicMock

from pytest import fixture, raises

from preacher.core.scenario.analysis import analyze_json_str
from preacher.core.scenario.extraction import Extractor


@fixture
def extract() -> Extractor:
    return MagicMock(return_value='value')


def test_jq(extract):
    analyzer = analyze_json_str(MagicMock(text='{"k1":"v1","k2":"v2"}'))
    value = analyzer.jq(extract)
    assert value == 'value'

    extract.assert_called_once_with({'k1': 'v1', 'k2': 'v2'})


def test_not_supported(extract):
    analyzer = analyze_json_str(MagicMock(text='{}'))
    with raises(NotImplementedError):
        analyzer.xpath(extract)
    with raises(NotImplementedError):
        analyzer.key(extract)

    extract.assert_not_called()
