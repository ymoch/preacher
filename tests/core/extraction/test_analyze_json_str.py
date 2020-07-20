from unittest.mock import Mock, NonCallableMock, sentinel

from pytest import fixture, raises

from preacher.core.extraction.analysis import analyze_json_str
from preacher.core.request import ResponseBody


@fixture
def extract():
    return Mock(return_value=sentinel.extracted)


def test_jq(extract):
    body = NonCallableMock(ResponseBody, text='{"k1":"v1","k2":"v2"}')
    analyzer = analyze_json_str(body)
    value = analyzer.jq(extract)
    assert value is sentinel.extracted

    extract.assert_called_once_with({'k1': 'v1', 'k2': 'v2'})


def test_key_for_invalid_body(extract):
    body = NonCallableMock(ResponseBody, text='[]')
    analyzer = analyze_json_str(body)
    with raises(ValueError):
        analyzer.key(extract)

    extract.assert_not_called()


def test_key_for_valid_body(extract):
    body = NonCallableMock(ResponseBody, text='{"int":1,"str":"s"}')
    analyzer = analyze_json_str(body)
    value = analyzer.key(extract)
    assert value is sentinel.extracted

    extract.assert_called_once_with({'int': 1, 'str': 's'})


def test_not_supported(extract):
    body = NonCallableMock(ResponseBody, text='{}')
    analyzer = analyze_json_str(body)
    with raises(NotImplementedError):
        analyzer.xpath(extract)

    extract.assert_not_called()
