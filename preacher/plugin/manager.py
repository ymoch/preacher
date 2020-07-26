"""Preacher plugin definitions."""

from pluggy import PluginManager

from . import hookspec
from . import impl

__all__ = ['get_plugin_manager']


def get_plugin_manager() -> PluginManager:
    """
    Get a plugin manager that the entry points and the default implementation are already loaded.
    """
    manager = PluginManager('preacher')
    manager.add_hookspecs(hookspec)
    manager.load_setuptools_entrypoints('preacher')
    manager.register(impl)
    return manager
