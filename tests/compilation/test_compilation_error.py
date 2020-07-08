from preacher.compilation.error import (
    CompilationError,
    IndexedNode,
    NamedNode,
    render_path,
)


def test_render_path():
    error = CompilationError('message')
    assert error.path == []
    assert error.render_path() == ''
    assert render_path(error.path) == ''

    error = error.on_node(IndexedNode(1))
    assert error.path == [IndexedNode(1)]
    assert error.render_path() == '[1]'
    assert render_path(error.path) == '[1]'

    error = CompilationError('message', node=None, child=error)
    assert error.path == [IndexedNode(1)]
    assert error.render_path() == '[1]'
    assert render_path(error.path) == '[1]'

    error = error.on_node(NamedNode('foo'))
    assert error.path == [NamedNode('foo'), IndexedNode(1)]
    assert error.render_path() == '.foo[1]'
    assert render_path(error.path) == '.foo[1]'
