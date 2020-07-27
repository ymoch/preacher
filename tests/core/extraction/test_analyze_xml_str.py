from unittest.mock import Mock, NonCallableMock

from pytest import fixture, raises

from preacher.core.extraction.analysis import analyze_xml_str
from preacher.core.extraction.error import ExtractionError
from preacher.core.request import ResponseBody

XML_VALUE = '''<?xml version="1.0" encoding="utf-8"?>
<foo>
    <bar attr-name="attr-value">bar-text</bar>
</foo>
'''


@fixture
def body():
    return NonCallableMock(ResponseBody, text=XML_VALUE, content=XML_VALUE.encode('utf-8'))


@fixture
def extract():
    return Mock(return_value='value')


def test_xpath(extract, body):
    analyzer = analyze_xml_str(body)
    value = analyzer.xpath(extract)
    assert value == 'value'

    extract.assert_called()


def test_jq(body):
    analyzer = analyze_xml_str(body)
    extract = Mock(side_effect=RuntimeError('msg'))
    with raises(RuntimeError):
        analyzer.jq(extract)


def test_key(extract, body):
    analyzer = analyze_xml_str(body)
    with raises(ExtractionError):
        analyzer.key(extract)

    extract.assert_not_called()
