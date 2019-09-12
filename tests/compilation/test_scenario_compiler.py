from unittest.mock import MagicMock, call, sentinel

from pytest import mark, raises

from preacher.compilation.case import CaseCompiler
from preacher.compilation.error import CompilationError
from preacher.compilation.scenario import ScenarioCompiler


@mark.parametrize('value, expected_suffix', (
    ({'label': []}, ': label'),
    ({'cases': ''}, ': cases'),
    ({'cases': ['']}, ': cases[0]'),
    ({'default': ''}, ': default'),
))
def test_when_given_invalid_values(value, expected_suffix):
    with raises(CompilationError) as error_info:
        ScenarioCompiler().compile(value)
    assert str(error_info.value).endswith(expected_suffix)


def test_when_given_an_empty_object():
    case_compiler = MagicMock(CaseCompiler)
    compiler = ScenarioCompiler(case_compiler=case_compiler)
    scenario = compiler.compile({})
    assert scenario.label is None
    assert list(scenario.cases()) == []

    case_compiler.of_default.assert_called_once_with({})


def test_generates_an_iterator_of_cases():
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
    assert scenario.label == 'label'
    assert list(scenario.cases()) == [sentinel.case, sentinel.case]

    case_compiler.of_default.assert_called_once_with({'a': 'b'})
    default_case_compiler.compile.assert_has_calls([
        call({}),
        call({'k': 'v'})],
    )
