from pytest import mark, raises

from preacher.core.extraction import JqExtractor, XPathExtractor
from preacher.compilation.extraction import compile
from preacher.compilation.error import CompilationError


def test_when_given_not_a_string():
    with raises(CompilationError) as error_info:
        compile({})
    assert str(error_info.value).endswith(' has 0')


@mark.parametrize('value, expected_query', (
    ('.foo', '.foo'),
    ({'jq': '.foo'}, '.foo'),
))
def test_when_given_a_jq(value, expected_query):
    extractor = compile('.foo')
    assert isinstance(extractor, JqExtractor)
    assert extractor.query == expected_query


def test_when_given_an_xpath():
    compiler = compile({'xpath': './foo'})
    assert isinstance(compiler, XPathExtractor)
    assert compiler.query == './foo'
