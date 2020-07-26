import sys
import uuid
from importlib.abc import InspectLoader
from importlib.machinery import ModuleSpec
from logging import Logger
from types import ModuleType
from unittest.mock import NonCallableMock, NonCallableMagicMock, sentinel

from pluggy import PluginManager
from pytest import fixture, raises

from preacher.plugin.loader import load_plugins

PKG = 'preacher.plugin.loader'


@fixture
def logger():
    return NonCallableMock(Logger)


def test_load_plugins_empty(logger):
    manager = NonCallableMock(PluginManager)
    load_plugins(manager, (), logger)
    manager.register.assert_not_called()


def test_load_plugins_normal(mocker, logger):
    loader = NonCallableMock(InspectLoader)

    spec = NonCallableMock(ModuleSpec, loader=loader)
    spec_ctor = mocker.patch(f'{PKG}.spec_from_file_location', return_value=spec)

    module = NonCallableMock(ModuleType)
    module_ctor = mocker.patch(f'{PKG}.module_from_spec', return_value=module)

    uuid4 = NonCallableMagicMock(uuid.uuid4)
    uuid4.__str__.return_value = 'module-name'
    mocker.patch('uuid.uuid4', return_value=uuid4)

    manager = NonCallableMock(PluginManager)
    load_plugins(manager, (sentinel.plugin,), logger)

    spec_ctor.assert_called_once_with('module-name', sentinel.plugin)
    module_ctor.assert_called_once_with(spec)
    loader.exec_module.assert_called_once_with(module)
    manager.register.assert_called_once_with(module)
    assert sys.modules['module-name'] == module


def test_load_plugins_not_a_module(mocker, logger):
    mocker.patch(f'{PKG}.spec_from_file_location', return_value=None)

    manager = NonCallableMock(PluginManager)
    with raises(RuntimeError):
        load_plugins(manager, (sentinel.plugin,), logger)

    manager.register.assert_not_called()


def test_load_plugins_invalid_module(mocker, logger):
    loader = NonCallableMock(InspectLoader)
    loader.exec_module.side_effect = SyntaxError('msg')

    spec = NonCallableMock(ModuleSpec, loader=loader)
    mocker.patch(f'{PKG}.spec_from_file_location', return_value=spec)

    module = NonCallableMock(ModuleType)
    mocker.patch(f'{PKG}.module_from_spec', return_value=module)

    uuid4 = NonCallableMagicMock(uuid.uuid4)
    uuid4.__str__.return_value = 'module-name'
    mocker.patch('uuid.uuid4', return_value=uuid4)

    manager = NonCallableMock(PluginManager)
    with raises(SyntaxError):
        load_plugins(manager, (sentinel.plugin,), logger)

    manager.register.assert_not_called()
    assert sys.modules.get('module-name') != module
