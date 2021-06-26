import itertools
from logging import Logger
from typing import Optional, Iterator, Iterable

from pluggy import PluginManager

from preacher.compilation.argument import Arguments
from preacher.core.scenario.scenario import Scenario
from .factory import create_scenario_compiler


def compile_scenarios(
    objs: Iterable[object],
    arguments: Optional[Arguments] = None,
    plugin_manager: Optional[PluginManager] = None,
    logger: Optional[Logger] = None,
) -> Iterator[Scenario]:
    compiler = create_scenario_compiler(plugin_manager=plugin_manager, logger=logger)
    return itertools.chain.from_iterable(
        compiler.compile_flattening(obj, arguments=arguments) for obj in objs
    )
