"""Preacher plugin definitions."""

from pluggy import PluginManager

from . import hookspec


def get_plugin_manager() -> PluginManager:
    manager = PluginManager('preacher')
    manager.add_hookspecs(hookspec)
    manager.load_setuptools_entrypoints('preacher')
    return manager
