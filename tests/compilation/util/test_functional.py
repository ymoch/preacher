from unittest.mock import Mock, call

from pytest import raises, mark

from preacher.compilation.error import CompilationError, NamedNode, IndexedNode
from preacher.compilation.util.functional import (
    map_compile,
    run_recursively,
    compile_flattening,
)


def succeeds(arg):
    return arg


def test_map_compile_for_empty_list():
    results = map_compile(lambda x: x, [])
    with raises(StopIteration):
        next(results)


def test_map_compile_for_successful_func():
    results = map_compile(lambda n: n * 2, [1, 2, 3])
    assert next(results) == 2
    assert next(results) == 4
    assert next(results) == 6


def test_map_compile_for_failing_func():
    child_error = CompilationError('message', node=NamedNode('key'))
    failing_func = Mock(side_effect=[1, child_error, 2])
    results = map_compile(failing_func, [3, 4, 5])
    assert next(results) == 1
    with raises(CompilationError) as error_info:
        next(results)
    assert error_info.value.path == [IndexedNode(1), NamedNode('key')]
    failing_func.assert_has_calls([call(3), call(4)])


@mark.parametrize('obj, expected_path', [
    ({1: 2}, []),
    ({'key': {1: 2}}, [NamedNode('key')]),
    ({'key': [1, '_error', 3]}, [NamedNode('key'), IndexedNode(1)]),
    ([1, {'key': '_error'}, 3], [IndexedNode(1), NamedNode('key')])
])
def test_run_recursively_with_invalid_obj(obj, expected_path):
    def _func(value):
        if value == '_error':
            raise CompilationError('message')

    with raises(CompilationError) as error_info:
        run_recursively(_func, obj)
    assert error_info.value.path == expected_path


@mark.parametrize('obj, expected', [
    ([], []),
    ([1, 2, [3, 4, {'k': 'v'}]], [2, 4, [6, 8, {'k': 'vv'}]]),
    ({}, {}),
    ({'k': 'v', 'foo': [1, [2, 3]]}, {'k': 'vv', 'foo': [2, [4, 6]]}),
    (1, 2),
])
def test_run_recursively_with_valid_obj(obj, expected):
    assert run_recursively(lambda x: x * 2, obj) == expected


def test_compile_flattening_error():
    def _compile(flag: bool) -> bool:
        if not flag:
            raise CompilationError('msg', node=NamedNode('x'))
        return not flag

    obj = [True, [[], [True, True, [False]]], True]
    compiled = compile_flattening(_compile, obj)
    assert not next(compiled)
    assert not next(compiled)
    assert not next(compiled)
    with raises(CompilationError) as error_info:
        next(compiled)
    assert error_info.value.path == [
        IndexedNode(1),
        IndexedNode(1),
        IndexedNode(2),
        IndexedNode(0),
        NamedNode('x'),
    ]
    with raises(StopIteration):
        next(compiled)


@mark.parametrize(('obj', 'expected'), [
    ([], []),
    ([[[]], [[[]]]], []),
    (1, [2]),
    ([1, [2, 3, [[4]]], [5, 6]], [2, 4, 6, 8, 10, 12])
])
def test_compile_flattening(obj, expected):
    assert list(compile_flattening(lambda x: x * 2, obj)) == expected
