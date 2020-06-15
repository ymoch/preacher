from typing import Callable, Mapping, TypeVar
from unittest.mock import MagicMock

from lxml.etree import _Element as Element
from pytest import raises

from preacher.core.scenario.analysis import Analyzer
from preacher.core.scenario.extraction import Extractor

T = TypeVar('T')


def test_incomplete_analyzer():
    class _IncompleteAnalyzer(Analyzer):
        def jq(self, extract: Callable[[object], T]) -> T:
            return super().jq(extract)

        def xpath(self, extract: Callable[[Element], T]) -> T:
            return super().xpath(extract)

        def key(self, extract: Callable[[Mapping], T]) -> T:
            return super().key(extract)

    analyzer = _IncompleteAnalyzer()

    with raises(NotImplementedError):
        analyzer.jq(MagicMock(Extractor))

    with raises(NotImplementedError):
        analyzer.xpath(MagicMock(Extractor))

    with raises(NotImplementedError):
        analyzer.key(MagicMock(Extractor))
