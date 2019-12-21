from typing import Callable, TypeVar
from unittest.mock import MagicMock

from lxml.etree import _Element as Element
from pytest import raises

from preacher.core.analysis import Analyzer
from preacher.core.extraction import Extractor

T = TypeVar('T')


def test_incomplete_analyzer():
    class _IncompleteAnalyzer(Analyzer):
        def jq(self, extract: Callable[[object], T]) -> T:
            return super().jq(extract)

        def xpath(self, extract: Callable[[Element], T]) -> T:
            return super().xpath(extract)

    analyzer = _IncompleteAnalyzer()

    with raises(NotImplementedError):
        analyzer.jq(MagicMock(Extractor))

    with raises(NotImplementedError):
        analyzer.xpath(MagicMock(Extractor))
