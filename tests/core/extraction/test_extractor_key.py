from unittest.mock import NonCallableMock

from pytest import fixture

from preacher.core.extraction.analysis import Analyzer
from preacher.core.extraction.extraction import KeyExtractor

DICTIONARY = {'int': 1, 'str': 'string'}


@fixture
def analyzer() -> Analyzer:
    analyzer = NonCallableMock(Analyzer)
    analyzer.for_mapping.side_effect = lambda x: x(DICTIONARY)
    return analyzer


def test_key_extractor(analyzer: Analyzer):
    assert KeyExtractor('invalid').extract(analyzer) is None
    assert KeyExtractor('invalid', cast=str).extract(analyzer) is None
    assert KeyExtractor('int').extract(analyzer) == 1
    assert KeyExtractor('int', cast=str).extract(analyzer) == '1'
    assert KeyExtractor('str').extract(analyzer) == 'string'
    assert KeyExtractor('str', multiple=True).extract(analyzer) == ['string']
