from dataclasses import dataclass
from datetime import datetime, timezone

from preacher.core.context import analyze_context
from preacher.core.extraction import JqExtractor


def test_analyze_context():

    @dataclass(frozen=True)
    class ComplexContext:
        value: object

    current = datetime(2019, 1, 2, 3, 4, 5, 678, tzinfo=timezone.utc)
    analyzer = analyze_context(ComplexContext(value=[current, 1, 'A']))
    assert JqExtractor('.value[0]').extract(analyzer) == (
        '2019-01-02T03:04:05.000678+00:00'
    )
    assert JqExtractor('.value[1]').extract(analyzer) == 1
    assert JqExtractor('.value[2]').extract(analyzer) == 'A'
