"""Preacher plugin definitions."""

from pluggy import PluginManager

from . import hookspec
from . import impl


def get_plugin_manager() -> PluginManager:
    manager = PluginManager('preacher')
    manager.add_hookspecs(hookspec)
    manager.load_setuptools_entrypoints('preacher')
    manager.register(impl)
    return manager
