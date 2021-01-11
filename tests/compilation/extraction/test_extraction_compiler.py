from typing import List, Tuple
from unittest.mock import Mock, call, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.extraction.extraction import ExtractionCompiler, add_default_extractions

PKG = 'preacher.compilation.extraction.extraction'


@fixture
def jq_factory():
    return Mock(return_value=sentinel.jq)


@fixture
def xpath_factory():
    return Mock(return_value=sentinel.xpath)


@fixture
def compiler(jq_factory, xpath_factory):
    compiler = ExtractionCompiler()
    compiler.add_factory('jq', jq_factory)
    compiler.add_factory('xpath', xpath_factory)
    return compiler


@mark.parametrize('value, expected_message, expected_path', (
    (1, '', []),
    ([], '', []),
    ({}, ' has 0', []),
    ({'jq': '.foo', 'xpath': 'bar'}, 'has 2', []),
    ({'jq': '.xxx', 'multiple': 1}, '', [NamedNode('multiple')]),
    ({'jq': '.foo', 'cast_to': 1}, ' string', [NamedNode('cast_to')]),
    ({'jq': '.foo', 'cast_to': 'xxx'}, ': xxx', [NamedNode('cast_to')]),
))
def test_when_given_not_a_string(compiler, value, expected_message, expected_path):
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert expected_message in str(error_info.value)
    assert error_info.value.path == expected_path


@mark.parametrize(('value', 'expected_call'), (
    (
        '.foo',
        call('.foo', multiple=False, cast=None)
    ),
    (
        {'jq': '.foo'},
        call('.foo', multiple=False, cast=None),
    ),
    (
        {'jq': '.bar', 'multiple': False, 'cast_to': 'int'},
        call('.bar', multiple=False, cast=int),
    ),
    (
        {'jq': '.bar', 'multiple': True, 'cast_to': 'float'},
        call('.bar', multiple=True, cast=float),
    ),
))
def test_when_given_a_jq(compiler, jq_factory, xpath_factory, value, expected_call):
    assert compiler.compile(value) is sentinel.jq
    jq_factory.assert_has_calls([expected_call])
    xpath_factory.assert_not_called()


@mark.parametrize(('value', 'expected_call'), (
    (
        {'xpath': '/foo'},
        call('/foo', multiple=False, cast=None),
    ),
    (
        {'xpath': './bar', 'multiple': False, 'cast_to': 'int'},
        call('./bar', multiple=False, cast=int),
    ),
))
def test_when_given_an_xpath(compiler, jq_factory, xpath_factory, value, expected_call):
    assert compiler.compile(value) is sentinel.xpath
    jq_factory.assert_not_called()
    xpath_factory.assert_has_calls([expected_call])


default_extraction_cases: List[Tuple[object, str, tuple]] = [
    ({'xpath': '/foo'}, 'XPathExtractor', call('/foo', multiple=False, cast=None)),
    ({'key': 'foo'}, 'KeyExtractor', call('foo', multiple=False, cast=None)),
]
try:  # When jq exists.
    import jq  # noqa: F401

    default_extraction_cases.append(
        ('.foo', 'JqExtractor', call('/foo', multiple=False, cast=None))
    )
    default_extraction_cases.append(
        ({'jq': '.foo'}, 'JqExtractor', call('/foo', multiple=False, cast=None))
    )
except ImportError:
    pass


@mark.parametrize(('value', 'expected_factory', 'expected_call'), default_extraction_cases)
def test_add_default_extractions(mocker, value, expected_factory, expected_call):
    factory = mocker.patch(f'{PKG}.{expected_factory}', return_value=sentinel.extraction)
    compiler = ExtractionCompiler()
    add_default_extractions(compiler)

    assert compiler.compile(value) is sentinel.extraction
    factory.assert_has_calls([expected_call])
