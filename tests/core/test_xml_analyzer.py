from unittest.mock import MagicMock

from pytest import fixture, mark

from preacher.core.analysis import analyze_xml_str
from preacher.core.extraction import Extractor


XML_VALUE = '''<?xml version="1.0"?>
<foo>
    <bar attr-name="attr-value">bar-text</bar>
</foo>
'''


@fixture
def extract() -> Extractor:
    return MagicMock(return_value='value')


@mark.xfail(raises=NotImplementedError)
def test_jq(extract):
    analyzer = analyze_xml_str(XML_VALUE)
    analyzer.jq(extract)

    extract.assert_not_called()


def test_xpath(extract):
    analyzer = analyze_xml_str(XML_VALUE)
    value = analyzer.xpath(extract)
    assert value == 'value'

    extract.assert_called()
