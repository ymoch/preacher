import json
from unittest.mock import NonCallableMock, sentinel

from pytest import fixture, mark, raises

from preacher.core.extraction.analysis import Analyzer
from preacher.core.extraction.error import ExtractionError
from preacher.core.extraction.impl.jq_ import JqExtractor, JqEngine, PyJqEngine


if PyJqEngine.is_available():

    VALUE = json.dumps({
        'foo': 'bar',
        'list': [
            {'key': 'value1'},
            {'key': 'value2'},
            {},
            {'key': 'value3'},
        ],
    }, separators=(',', ':'))

    def test_extract_invalid():
        engine = PyJqEngine()
        with raises(ExtractionError) as error_info:
            engine.iter('xxx', VALUE)
        assert str(error_info.value).endswith(': xxx')

    @mark.parametrize(('query', 'expected'), [
        ('.xxx', [None]),
        ('.foo', ['bar']),
        ('.list[].key', ['value1', 'value2', None, 'value3']),
    ])
    def test_extract_multiple(query, expected):
        engine = PyJqEngine()
        assert list(engine.iter(query, VALUE)) == expected


@fixture
def analyzer():
    analyzer = NonCallableMock(Analyzer)
    analyzer.for_text.side_effect = lambda extract: extract(sentinel.text)
    return analyzer


@mark.parametrize(('values', 'cast', 'multiple', 'expected'), (
    ([], None, False, None),
    ([], int, False, None),
    ([], None, True, []),
    ([], int, True, []),
    (['1', '2'], None, False, '1'),
    (['1', '2'], int, False, 1),
    (['1', None, 2], None, True, ['1', None, 2]),
    (['1', None, 2], int, True, [1, None, 2]),
))
def test_extract_single(analyzer, values, cast, multiple, expected):
    engine = NonCallableMock(JqEngine)
    engine.iter.return_value = iter(values)

    extractor = JqExtractor(engine, sentinel.query, cast=cast, multiple=multiple)
    assert extractor.extract(analyzer) == expected

    engine.iter.assert_called_once_with(sentinel.query, sentinel.text)
