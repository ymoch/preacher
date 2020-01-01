from unittest.mock import MagicMock

from pytest import raises

from preacher.compilation.error import CompilationError, NamedNode, IndexedNode
from preacher.compilation.util import map_compile
from preacher.core.util.functional import identify


def succeeds(arg):
    return arg


def test_map_compile():
    results = map_compile(identify, [])
    with raises(StopIteration):
        next(results)

    results = map_compile(lambda n: n * 2, [1, 2, 3])
    assert next(results) == 2
    assert next(results) == 4
    assert next(results) == 6

    child_error = CompilationError('message', path=[NamedNode('key')])
    failure_func = MagicMock(side_effect=[1, child_error, 2])
    results = map_compile(failure_func, [3, 4, 4])
    assert next(results) == 1
    with raises(CompilationError) as error_info:
        next(results)
    assert error_info.value.path == [IndexedNode(1), NamedNode('key')]
