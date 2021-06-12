import os
from io import StringIO
from tempfile import TemporaryDirectory

from pytest import fixture, raises

from preacher.compilation.yaml.integration import load_from_paths


@fixture
def base_dir():
    with TemporaryDirectory() as path:
        with open(os.path.join(path, 'foo.yml'), 'w') as f:
            f.write('foo')
        with open(os.path.join(path, 'bar.yml'), 'w') as f:
            f.write('bar')
        yield path


def test_load_objs_empty(mocker):
    mocker.patch('sys.stdin', StringIO('foo\n---\nbar'))

    paths = ()
    objs = load_from_paths(paths)

    assert next(objs) == 'foo'
    assert next(objs) == 'bar'
    with raises(StopIteration):
        next(objs)


def test_load_objs_filled(base_dir):
    paths = (os.path.join(base_dir, 'foo.yml'), os.path.join(base_dir, 'bar.yml'))
    objs = load_from_paths(paths)

    assert next(objs) == 'foo'
    assert next(objs) == 'bar'
    with raises(StopIteration):
        next(objs)
