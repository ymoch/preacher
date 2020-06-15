from unittest.mock import MagicMock, sentinel

from pytest import fixture, raises

from preacher.core.scenario.analysis import analyze_json_str


@fixture
def extract():
    return MagicMock(return_value=sentinel.extracted)


def test_jq(extract):
    analyzer = analyze_json_str(MagicMock(text='{"k1":"v1","k2":"v2"}'))
    value = analyzer.jq(extract)
    assert value is sentinel.extracted

    extract.assert_called_once_with({'k1': 'v1', 'k2': 'v2'})


def test_key_for_invalid_body(extract):
    analyzer = analyze_json_str(MagicMock(text='[]'))
    with raises(ValueError):
        analyzer.key(extract)

    extract.assert_not_called()


def test_key_for_valid_body(extract):
    analyzer = analyze_json_str(MagicMock(text='{"int":1, "str":"s"}'))
    value = analyzer.key(extract)
    assert value is sentinel.extracted

    extract.assert_called_once_with({'int': 1, 'str': 's'})


def test_not_supported(extract):
    analyzer = analyze_json_str(MagicMock(text='{}'))
    with raises(NotImplementedError):
        analyzer.xpath(extract)

    extract.assert_not_called()
