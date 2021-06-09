from typing import Optional

from pluggy import PluginManager

from preacher.compilation.yaml.loader import Loader


def create_yaml_loader(plugin_manager: Optional[PluginManager] = None) -> Loader:
    loader = Loader()
    if plugin_manager:
        plugin_manager.hook.preacher_modify_yaml_loader(loader=loader)
    return loader
