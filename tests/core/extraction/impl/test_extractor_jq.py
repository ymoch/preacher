from unittest.mock import NonCallableMock, sentinel

from pytest import fixture, mark

from preacher.core.extraction.analysis import Analyzer
from preacher.core.extraction.impl.jq_ import JqExtractor, JqEngine


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
