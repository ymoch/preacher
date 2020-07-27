from unittest.mock import Mock, NonCallableMock, sentinel

from pytest import fixture, raises

from preacher.core.extraction.analysis import ResponseBodyAnalyzer
from preacher.core.extraction.error import ExtractionError
from preacher.core.request import ResponseBody


@fixture
def extract():
    return Mock(return_value=sentinel.extracted)


def test_for_text(extract):
    body = NonCallableMock(ResponseBody, text='{"k1":"v1","k2":"v2"}')
    analyzer = ResponseBodyAnalyzer(body)
    value = analyzer.for_text(extract)
    assert value is sentinel.extracted

    extract.assert_called_once_with('{"k1":"v1","k2":"v2"}')


def test_for_mapping_on_invalid_body(extract):
    body = NonCallableMock(ResponseBody, text='[]')
    analyzer = ResponseBodyAnalyzer(body)
    with raises(ExtractionError):
        analyzer.for_mapping(extract)

    extract.assert_not_called()


def test_for_mapping_on_valid_body(extract):
    body = NonCallableMock(ResponseBody, text='{"int":1,"str":"s"}')
    analyzer = ResponseBodyAnalyzer(body)
    value = analyzer.for_mapping(extract)
    assert value is sentinel.extracted

    extract.assert_called_once_with({'int': 1, 'str': 's'})


def test_for_etree(extract):
    body = NonCallableMock(ResponseBody, content=b'{}')
    analyzer = ResponseBodyAnalyzer(body)
    with raises(ExtractionError):
        analyzer.for_etree(extract)

    extract.assert_not_called()
