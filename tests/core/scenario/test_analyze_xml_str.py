from unittest.mock import Mock, NonCallableMock

from pytest import fixture, raises

from preacher.core.scenario.analysis import analyze_xml_str
from preacher.core.scenario.request import ResponseBody

XML_VALUE = '''<?xml version="1.0" encoding="utf-8"?>
<foo>
    <bar attr-name="attr-value">bar-text</bar>
</foo>
'''.encode('utf-8')


@fixture
def body():
    return NonCallableMock(ResponseBody, content=XML_VALUE)


@fixture
def extract():
    return Mock(return_value='value')


def test_xpath(extract, body):
    analyzer = analyze_xml_str(body)
    value = analyzer.xpath(extract)
    assert value == 'value'

    extract.assert_called()


def test_not_supported(extract, body):
    analyzer = analyze_xml_str(body)
    with raises(NotImplementedError):
        analyzer.jq(extract)
    with raises(NotImplementedError):
        analyzer.key(extract)

    extract.assert_not_called()
