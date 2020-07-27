from typing import Callable, Mapping, TypeVar
from unittest.mock import Mock

from lxml.etree import _Element as Element
from pytest import raises

from preacher.core.extraction.analysis import Analyzer

T = TypeVar('T')


def test_analyzer_interface():
    class _IncompleteAnalyzer(Analyzer):
        def for_text(self, extract: Callable[[str], T]) -> T:
            return super().for_text(extract)

        def for_etree(self, extract: Callable[[Element], T]) -> T:
            return super().for_etree(extract)

        def for_mapping(self, extract: Callable[[Mapping], T]) -> T:
            return super().for_mapping(extract)

    analyzer = _IncompleteAnalyzer()
    ext = Mock()
    with raises(NotImplementedError):
        analyzer.for_text(ext)
    with raises(NotImplementedError):
        analyzer.for_etree(ext)
    with raises(NotImplementedError):
        analyzer.for_mapping(ext)

    ext.assert_not_called()
