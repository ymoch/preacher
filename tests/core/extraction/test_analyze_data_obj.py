from dataclasses import dataclass
from datetime import datetime, timezone

from pytest import raises

from preacher.core.extraction.analysis import analyze_data_obj
from preacher.core.extraction.error import ExtractionError
from preacher.core.extraction.extraction import JqExtractor, XPathExtractor, KeyExtractor


@dataclass(frozen=True)
class Context:
    value: object


def test_analyze_data_obj_jq():
    current = datetime(2019, 1, 2, 3, 4, 5, 678, tzinfo=timezone.utc)
    analyzer = analyze_data_obj(Context(value=[current, 1, 'A']))
    assert JqExtractor('.value[0]').extract(analyzer) == (
        '2019-01-02T03:04:05.000678+00:00'
    )
    assert JqExtractor('.value[1]').extract(analyzer) == 1
    assert JqExtractor('.value[2]').extract(analyzer) == 'A'


def test_analyze_data_obj_not_xpath():
    content = Context(value=1)
    analyzer = analyze_data_obj(content)
    with raises(ExtractionError):
        XPathExtractor('/value').extract(analyzer)


def test_analyze_data_obj_key():
    content = Context(value=1)
    analyzer = analyze_data_obj(content)
    assert KeyExtractor('value').extract(analyzer) == 1
