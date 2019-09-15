from unittest.mock import MagicMock

from pytest import fixture, mark

from preacher.core.analysis import analyze_json_str
from preacher.core.extraction import Extractor


@fixture
def extract() -> Extractor:
    return MagicMock(return_value='value')


def test_jq(extract):
    analyzer = analyze_json_str('{"k1":"v1","k2":"v2"}')
    value = analyzer.jq(extract)
    assert value == 'value'

    extract.assert_called_once_with({'k1': 'v1', 'k2': 'v2'})


@mark.xfail(raises=NotImplementedError)
def test_xpath(extract):
    analyzer = analyze_json_str('{}')
    analyzer.xpath(extract)

    extract.assert_not_called()
