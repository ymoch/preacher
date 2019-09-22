from pytest import mark, raises

from preacher.core.extraction import JqExtractor, XPathExtractor
from preacher.compilation.extraction import ExtractionCompiler
from preacher.compilation.error import CompilationError


@mark.parametrize('value, expected_suffix', (
    ({}, ' has 0'),
    ({'jq': '.xxx', 'multiple': 1}, ': multiple'),
))
def test_when_given_not_a_string(value, expected_suffix):
    with raises(CompilationError) as error_info:
        ExtractionCompiler().compile(value)
    assert str(error_info.value).endswith(expected_suffix)


@mark.parametrize('value, expected_query, expected_multiple', (
    ('.foo', '.foo', False),
    ({'jq': '.foo'}, '.foo', False),
    ({'jq': '.bar', 'multiple': False}, '.bar', False),
    ({'jq': '.bar', 'multiple': True}, '.bar', True),
))
def test_when_given_a_jq(value, expected_query, expected_multiple):
    extractor = ExtractionCompiler().compile(value)
    assert isinstance(extractor, JqExtractor)
    assert extractor.query == expected_query
    assert extractor.multiple == expected_multiple


@mark.parametrize('value, expected_query, expected_multiple', (
    ({'xpath': './foo'}, './foo', False),
    ({'xpath': './foo', 'multiple': False}, './foo', False),
    ({'xpath': './foo', 'multiple': True}, './foo', True),
))
def test_when_given_an_xpath(value, expected_query, expected_multiple):
    extractor = ExtractionCompiler().compile(value)
    assert isinstance(extractor, XPathExtractor)
    assert extractor.query == expected_query
    assert extractor.multiple == expected_multiple
