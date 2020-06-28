from unittest.mock import Mock, NonCallableMock, sentinel

from pytest import mark

from preacher.compilation.yaml import load_from_path


@mark.parametrize('path, expected_origin', [
    ('scenario.yml', ''),
    ('/scenario.yml', '/'),
    ('/path/to/scenario.yml', '/path/to'),
    ('./scenario.yml', '.'),
    ('./path/to/scenario.yml', './path/to'),
])
def test_load_from_path(path, expected_origin, mocker):
    open_mock_entering = NonCallableMock(
        __enter__=Mock(return_value=sentinel.io),
        __exit__=Mock(),
    )
    open_mock = mocker.patch('builtins.open', return_value=open_mock_entering)

    load_mock = mocker.patch('preacher.compilation.yaml.load')
    load_mock.return_value = sentinel.obj

    actual = load_from_path(path)
    assert actual is sentinel.obj

    open_mock_entering.__enter__.assert_called_once()
    open_mock_entering.__exit__.assert_called_once()
    open_mock.assert_called_once_with(path)
    load_mock.assert_called_once_with(sentinel.io, expected_origin)
