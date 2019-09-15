from unittest.mock import MagicMock

from pytest import fixture, mark

from preacher.core.extraction import JqExtractor


VALUE = {'foo': 'bar'}


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
    actual = extractor.extract(analyzer)
    assert actual == expected
