from unittest.mock import MagicMock

from pytest import raises

from preacher.core.analysis import Analyzer
from preacher.core.extraction import Extractor


def test_incomplete_extractor():
    class _IncompleteExtractor(Extractor):
        def extract(self, analyzer: Analyzer) -> object:
            return super().extract(analyzer)
    with raises(NotImplementedError):
        _IncompleteExtractor().extract(MagicMock(Analyzer))
