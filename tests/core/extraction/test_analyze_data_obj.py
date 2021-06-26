from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping
from unittest.mock import sentinel

from lxml.etree import _Element as Element
from pytest import raises

from preacher.core.extraction.analysis import analyze_data_obj
from preacher.core.extraction.error import ExtractionError


@dataclass(frozen=True)
class Context:
    value: object


def test_analyze_data_obj_for_text():
    current = datetime(2019, 1, 2, 3, 4, 5, 678, tzinfo=timezone.utc)
    analyzer = analyze_data_obj(Context(value=[current, 1, "A"]))

    def _extract(value: str) -> object:
        assert value == '{"value":["2019-01-02T03:04:05.000678+00:00",1,"A"]}'
        return sentinel.extracted

    assert analyzer.for_text(_extract) is sentinel.extracted


def test_analyze_data_obj_for_mapping():
    content = Context(value=1)
    analyzer = analyze_data_obj(content)

    def _extract(value: Mapping) -> object:
        assert value == {"value": 1}
        return sentinel.extracted

    assert analyzer.for_mapping(_extract) is sentinel.extracted


def test_analyze_data_obj_for_etree():
    content = Context(value=1)
    analyzer = analyze_data_obj(content)

    def _extract(_: Element) -> object:
        return sentinel.extracted

    with raises(ExtractionError):
        analyzer.for_etree(_extract)
