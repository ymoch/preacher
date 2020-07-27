from typing import Callable, Mapping, TypeVar
from unittest.mock import Mock

from lxml.etree import _Element as Element
from pytest import raises

from preacher.core.extraction.analysis import Analyzer

T = TypeVar('T')


def test_incomplete_analyzer():
    class _IncompleteAnalyzer(Analyzer):
        def jq_text(self, extract: Callable[[str], T]) -> T:
            return super().jq_text(extract)

        def xpath(self, extract: Callable[[Element], T]) -> T:
            return super().xpath(extract)

        def key(self, extract: Callable[[Mapping], T]) -> T:
            return super().key(extract)

    analyzer = _IncompleteAnalyzer()
    ext = Mock()
    with raises(NotImplementedError):
        analyzer.jq_text(ext)
    with raises(NotImplementedError):
        analyzer.xpath(ext)
    with raises(NotImplementedError):
        analyzer.key(ext)

    ext.assert_not_called()
