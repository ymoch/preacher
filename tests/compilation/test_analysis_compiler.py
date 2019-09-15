from pytest import mark, raises

from preacher.compilation.analysis import AnalysisCompiler
from preacher.compilation.error import CompilationError


@mark.parametrize('value, expected_suffix', (
    ([], ''),
    ({}, ''),
    ('invalid', ': invalid'),
))
def test_given_invalid_keys(value, expected_suffix):
    compiler = AnalysisCompiler()
    with raises(CompilationError) as error_info:
        compiler.compile(value)

    assert str(error_info.value).endswith(expected_suffix)


@mark.parametrize('value, text', (
    ('json', '{"key": "value"}'),
    ('xml', '<a><b>text1</b><b>text2</b></a>'),
))
def test_given_valid_keys(value, text):
    compiler = AnalysisCompiler()
    analyze = compiler.compile(value)
    analyze(text)
