from unittest.mock import MagicMock, call, patch, sentinel

from pytest import mark, raises

from preacher.compilation.case import CaseCompiler
from preacher.compilation.error import CompilationError
from preacher.compilation.scenario import ScenarioCompiler


CONSTRUCTOR = 'preacher.compilation.scenario.Scenario'


@mark.parametrize('value, expected_suffix', (
    ('', ''),
    ({'label': []}, ': label'),
    ({'cases': ''}, ': cases'),
    ({'cases': ['']}, ': cases[0]'),
    ({'default': ''}, ': default'),
))
def test_when_given_invalid_values(value, expected_suffix):
    with raises(CompilationError) as error_info:
        ScenarioCompiler().compile(value)
    assert str(error_info.value).endswith(expected_suffix)


@patch(CONSTRUCTOR, return_value=sentinel.scenario)
def test_given_an_empty_object(ctor):
    case_compiler = MagicMock(CaseCompiler)
    compiler = ScenarioCompiler(case_compiler=case_compiler)
    scenario = compiler.compile({})

    assert scenario is sentinel.scenario
    ctor.assert_called_once_with(label=None, cases=[])

    case_compiler.of_default.assert_called_once_with({})


@patch(CONSTRUCTOR, return_value=sentinel.scenario)
def test_given_a_filled_object(ctor):
    default_case_compiler = MagicMock(
        CaseCompiler,
        compile=MagicMock(return_value=sentinel.case),
    )
    case_compiler = MagicMock(
        CaseCompiler,
        of_default=MagicMock(return_value=default_case_compiler),
    )
    compiler = ScenarioCompiler(case_compiler=case_compiler)
    scenario = compiler.compile({
        'label': 'label',
        'default': {'a': 'b'},
        'cases': [{}, {'k': 'v'}],
    })
    assert scenario is sentinel.scenario
    ctor.assert_called_once_with(
        label='label',
        cases=[sentinel.case, sentinel.case],
    )

    case_compiler.of_default.assert_called_once_with({'a': 'b'})
    default_case_compiler.compile.assert_has_calls([
        call({}),
        call({'k': 'v'})],
    )
