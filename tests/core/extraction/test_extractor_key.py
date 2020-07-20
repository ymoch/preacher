from unittest.mock import Mock, NonCallableMock

from pytest import fixture

from preacher.core.extraction.analysis import Analyzer
from preacher.core.extraction.extraction import KeyExtractor

DICTIONARY = {
    'int': 1,
    'str': 'string',
}


@fixture
def analyzer() -> Analyzer:
    return NonCallableMock(
        spec=Analyzer,
        key=Mock(side_effect=lambda x: x(DICTIONARY)),
    )


def test_key_extractor(analyzer: Analyzer):
    assert KeyExtractor('invalid').extract(analyzer) is None
    assert KeyExtractor('int').extract(analyzer) == 1
    assert KeyExtractor('str').extract(analyzer) == 'string'
