from pytest import mark, raises

from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.parameter import compile_parameter


@mark.parametrize('obj, expected_path', [
    ('', []),
    ({'label': []}, [NamedNode('label')]),
    ({'label': {}}, [NamedNode('label')]),
    ({'args': ''}, [NamedNode('args')]),
    ({'args': []}, [NamedNode('args')]),
])
def test_given_invalid_obj(obj, expected_path):
    with raises(CompilationError) as error_info:
        compile_parameter(obj)
    assert error_info.value.path == expected_path


def test_given_empty_mapping():
    parameter = compile_parameter({})
    assert parameter.label is None
    assert parameter.arguments == {}


def test_given_filled_mapping():
    parameter = compile_parameter({'label': 'foo', 'args': {'k': 'v'}})
    assert parameter.label == 'foo'
    assert parameter.arguments == {'k': 'v'}
