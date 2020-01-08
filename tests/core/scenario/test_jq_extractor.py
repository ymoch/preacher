from unittest.mock import MagicMock

from pytest import fixture, mark, raises

from preacher.core.scenario.extraction import JqExtractor, EvaluationError
from preacher.core.scenario.util.functional import identify

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
    ],
    'int_string': '10',
    'int_strings': [
        {'value': '1'},
        {},
        {'value': '2'},
    ],
}


@fixture
def analyzer():
    return MagicMock(
        jq=MagicMock(side_effect=lambda x: x(VALUE))
    )


def test_extract_invalid(analyzer):
    extractor = JqExtractor(query='xxx')
    with raises(EvaluationError) as error_info:
        extractor.extract(analyzer)
    assert str(error_info.value).endswith(': xxx')


@mark.parametrize('query, expected', (
    ('.xxx', None),
    ('.foo', 'bar'),
    ('.int_string', '10'),
))
def test_extract_default(query, expected, analyzer):
    extractor = JqExtractor(query)
    assert extractor.extract(analyzer) == expected


@mark.parametrize('query, multiple, cast, expected', (
    ('.xxx', False, identify, None),
    ('.foo', False, identify, 'bar'),
    ('.int_string', False, identify, '10'),
    ('.xxx', True, identify, [None]),
    ('.foo', True, identify, ['bar']),
    ('.list[].key', True, identify, ['value1', 'value2', None, 'value3']),
    ('.int_string', False, int, 10),
    ('.int_strings[].value', False, int, 1),
    ('.int_strings[].value', True, int, [1, None, 2]),
))
def test_extract_multiple(query, multiple, cast, expected, analyzer):
    extractor = JqExtractor(query, multiple=multiple, cast=cast)
    assert extractor.extract(analyzer) == expected
