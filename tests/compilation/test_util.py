from unittest.mock import MagicMock, call

from pytest import raises

from preacher.compilation.error import CompilationError, NamedNode, IndexedNode
from preacher.compilation.util import map_compile, for_each
from preacher.core.util.functional import identify


def succeeds(arg):
    return arg


def test_map_compile_for_empty_list():
    results = map_compile(identify, [])
    with raises(StopIteration):
        next(results)


def test_map_compile_for_successful_func():
    results = map_compile(lambda n: n * 2, [1, 2, 3])
    assert next(results) == 2
    assert next(results) == 4
    assert next(results) == 6


def test_map_compile_for_failing_func():
    child_error = CompilationError('message', path=[NamedNode('key')])
    failing_func = MagicMock(side_effect=[1, child_error, 2])
    results = map_compile(failing_func, [3, 4, 5])
    assert next(results) == 1
    with raises(CompilationError) as error_info:
        next(results)
    assert error_info.value.path == [IndexedNode(1), NamedNode('key')]
    failing_func.assert_has_calls([call(3), call(4)])


def test_for_each_for_empty_list():
    func = MagicMock()
    for_each(identify, [])
    func.assert_not_called()


def test_for_each_for_successful_func():
    func = MagicMock()
    for_each(func, [1, 2, 3])
    func.assert_has_calls([call(1), call(2), call(3)])


def test_for_each_for_failing_func():
    child_error = CompilationError('message', path=[NamedNode('key')])
    failing_func = MagicMock(side_effect=[1, child_error, 2])
    with raises(CompilationError) as error_info:
        for_each(failing_func, [3, 4, 5])
    assert error_info.value.path == [IndexedNode(1), NamedNode('key')]
    failing_func.assert_has_calls([call(3), call(4)])
