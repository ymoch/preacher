from unittest.mock import NonCallableMock, sentinel

from preacher.compilation.scenario.integration import compile_scenarios
from preacher.compilation.scenario.scenario import ScenarioCompiler

PKG = "preacher.compilation.scenario.integration"


def test_compile_scenario(mocker):
    compiler = NonCallableMock(ScenarioCompiler)
    compiler.compile_flattening.return_value = iter([sentinel.scenario])
    compiler_ctor = mocker.patch(f"{PKG}.create_scenario_compiler", return_value=compiler)

    scenarios = compile_scenarios(
        iter([sentinel.objs]),
        arguments=sentinel.args,
        plugin_manager=sentinel.plugin_manager,
        logger=sentinel.logger,
    )
    assert list(scenarios) == [sentinel.scenario]

    compiler_ctor.assert_called_once_with(
        plugin_manager=sentinel.plugin_manager,
        logger=sentinel.logger,
    )
    compiler.compile_flattening.assert_called_once_with(sentinel.objs, arguments=sentinel.args)
