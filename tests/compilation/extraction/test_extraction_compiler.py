from unittest.mock import call

from pytest import mark, raises

from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.extraction.extraction import ExtractionCompiler, add_default_extractions

PKG = 'preacher.compilation.extraction.extraction'


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
    compiler = ExtractionCompiler()
    add_default_extractions(compiler)
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert expected_message in str(error_info.value)
    assert error_info.value.path == expected_path


@mark.parametrize('value, expected_ctor, expected_call', (
    (
        '.foo',
        'JqExtractor',
        call('.foo', multiple=False, cast=None)
    ),
    (
        {'jq': '.foo'},
        'JqExtractor',
        call('.foo', multiple=False, cast=None),
    ),
    (
        {'jq': '.bar', 'multiple': False, 'cast_to': 'int'},
        'JqExtractor',
        call('.bar', multiple=False, cast=int),
    ),
    (
        {'jq': '.bar', 'multiple': True, 'cast_to': 'float'},
        'JqExtractor',
        call('.bar', multiple=True, cast=float),
    ),
    (
        {'xpath': './foo'},
        'XPathExtractor',
        call('./foo', multiple=False, cast=None),
    ),
    (
        {'xpath': './foo', 'multiple': False},
        'XPathExtractor',
        call('./foo', multiple=False, cast=None),
    ),
    (
        {'xpath': './foo', 'multiple': True, 'cast_to': 'string'},
        'XPathExtractor',
        call('./foo', multiple=True, cast=str),
    ),
    (
        {'key': 'foo'},
        'KeyExtractor',
        call('foo', multiple=False, cast=None),
    ),
    (
        {'key': 'bar', 'multiple': True, 'cast_to': 'float'},
        'KeyExtractor',
        call('bar', multiple=True, cast=float),
    ),
))
def test_when_given_a_valid_value(value, expected_ctor, expected_call, mocker):
    ctor = mocker.patch(f'{PKG}.{expected_ctor}')
    compiler = ExtractionCompiler()
    add_default_extractions(compiler)
    compiler.compile(value)
    ctor.assert_has_calls([expected_call])
