from unittest.mock import MagicMock, patch, sentinel

from pytest import mark

from preacher.compilation.yaml import load_from_path


@mark.parametrize('path, expected_origin', [
    ('scenario.yml', ''),
    ('/scenario.yml', '/'),
    ('/path/to/scenario.yml', '/path/to'),
    ('./scenario.yml', '.'),
    ('./path/to/scenario.yml', './path/to'),
])
@patch('preacher.compilation.yaml.load', return_value=sentinel.obj)
@patch('builtins.open')
def test_load_from_path(open_mock, load_mock, path, expected_origin):
    open_mock_entering = MagicMock(
        __enter__=MagicMock(return_value=sentinel.io)
    )
    open_mock.return_value = open_mock_entering

    actual = load_from_path(path)
    assert actual is sentinel.obj

    open_mock.assert_called_once_with(path)
    load_mock.assert_called_once_with(sentinel.io, expected_origin)
