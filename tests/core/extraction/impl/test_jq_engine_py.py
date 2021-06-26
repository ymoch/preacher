import json

from pytest import mark, raises

from preacher.core.extraction import ExtractionError
from preacher.core.extraction.impl.jq_engine import PyJqEngine

VALUE = json.dumps(
    {
        "foo": "bar",
        "list": [
            {"key": "value1"},
            {"key": "value2"},
            {},
            {"key": "value3"},
        ],
    },
    separators=(",", ":"),
)

if PyJqEngine.is_available():

    def test_given_an_invalid_query():
        engine = PyJqEngine()
        with raises(ExtractionError) as error_info:
            engine.iter("xxx", VALUE)
        assert str(error_info.value).endswith(": xxx")

    @mark.parametrize(
        ("query", "expected"),
        [
            (".xxx", [None]),
            (".foo", ["bar"]),
            (".list[].key", ["value1", "value2", None, "value3"]),
        ],
    )
    def test_given_a_valid_query(query, expected):
        engine = PyJqEngine()
        assert list(engine.iter(query, VALUE)) == expected
