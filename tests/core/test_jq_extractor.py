from unittest.mock import MagicMock

from pytest import fixture, mark

from preacher.core.extraction import JqExtractor


VALUE = {
    'foo': 'bar',
    'list': [
        {
            "key": "value1",
        },
        {
            "key": "value2",
        },
        {},
        {
            "key": "value3",
        },
    ]
}


@fixture
def analyzer():
    return MagicMock(
        jq=MagicMock(side_effect=lambda x: x(VALUE))
    )


@mark.parametrize('query, expected', (
    ('.xxx', None),
    ('.foo', 'bar'),
))
def test_extract(query, expected, analyzer):
    extractor = JqExtractor(query)
    assert extractor.query == query
    assert not extractor.multiple

    actual = extractor.extract(analyzer)
    assert actual == expected


@mark.parametrize('query, expected', (
    ('.xxx', [None]),
    ('.foo', ['bar']),
    ('.list[].key', ['value1', 'value2', None, 'value3'])
))
def test_extract_multiple(query, expected, analyzer):
    extractor = JqExtractor(query, multiple=True)
    assert extractor.query == query
    assert extractor.multiple

    actual = extractor.extract(analyzer)
    assert actual == expected
