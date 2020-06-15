from unittest.mock import MagicMock

from pytest import fixture, raises

from preacher.core.scenario.analysis import analyze_xml_str
from preacher.core.scenario.extraction import Extractor
from preacher.core.scenario.request import ResponseBody

XML_VALUE = '''<?xml version="1.0" encoding="utf-8"?>
<foo>
    <bar attr-name="attr-value">bar-text</bar>
</foo>
'''.encode('utf-8')


@fixture
def response_body():
    return MagicMock(ResponseBody, content=XML_VALUE)


@fixture
def extract():
    return MagicMock(Extractor, return_value='value')


def test_xpath(extract, response_body):
    analyzer = analyze_xml_str(response_body)
    value = analyzer.xpath(extract)
    assert value == 'value'

    extract.assert_called()


def test_not_supported(extract, response_body):
    analyzer = analyze_xml_str(response_body)
    with raises(NotImplementedError):
        analyzer.jq(extract)
    with raises(NotImplementedError):
        analyzer.key(extract)

    extract.assert_not_called()
