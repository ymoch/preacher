from unittest.mock import MagicMock, call, patch, sentinel

from pytest import mark, raises, fixture

from preacher.compilation.case import CaseCompiler
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.scenario import ScenarioCompiler


CONSTRUCTOR = 'preacher.compilation.scenario.Scenario'


@fixture
def description():
    compiler = MagicMock(spec=DescriptionCompiler)
    compiler.compile.return_value = sentinel.description
    return compiler


@fixture
def case(case_of_default):
    compiler = MagicMock(spec=CaseCompiler)
    compiler.of_default.return_value = case_of_default
    return compiler


@fixture
def case_of_default(sub_case):
    compiler = MagicMock(spec=CaseCompiler)
    compiler.compile.return_value = sentinel.case
    compiler.of_default.return_value = sub_case
    return compiler


@fixture
def sub_case():
    compiler = MagicMock(spec=CaseCompiler)
    compiler.compile.return_value = sentinel.sub_case
    return compiler


@mark.parametrize('value, expected_path', (
    ('', []),
    ({'label': []}, [NamedNode('label')]),
    ({'cases': ''}, [NamedNode('cases')]),
    ({'subscenarios': ''}, [NamedNode('subscenarios')]),
    ({'default': ''}, [NamedNode('default')]),
))
def test_when_given_invalid_values(value, expected_path, description, case):
    compiler = ScenarioCompiler(description=description, case=case)
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert error_info.value.path == expected_path


@patch(CONSTRUCTOR, return_value=sentinel.scenario)
def test_given_an_empty_object(ctor, description, case):
    compiler = ScenarioCompiler(description=description, case=case)
    scenario = compiler.compile({})

    assert scenario is sentinel.scenario
    ctor.assert_called_once_with(
        label=None,
        conditions=[],
        cases=[],
        subscenarios=[],
    )

    case.of_default.assert_called_once_with({})


@patch(CONSTRUCTOR, return_value=sentinel.scenario)
def test_given_a_filled_object(
    ctor,
    description,
    case,
    case_of_default,
    sub_case
):
    compiler = ScenarioCompiler(description=description, case=case)
    scenario = compiler.compile({
        'label': 'label',
        'default': {'a': 'b'},
        'when': {'c': 'd'},
        'cases': [{}, {'k': 'v'}],
        'subscenarios': [
            {
                'label': 'sublabel',
                'default': {'c': 'd'},
                'cases': [{'sub_k': 'sub_v'}]
            },
        ],
    })
    assert scenario is sentinel.scenario
    ctor.assert_has_calls([
        call(
            label='sublabel',
            conditions=[],
            cases=[sentinel.sub_case],
            subscenarios=[],
        ),
        call(
            label='label',
            conditions=[sentinel.description],
            cases=[sentinel.case, sentinel.case],
            subscenarios=[sentinel.scenario],
        ),
    ])

    case.of_default.assert_called_once_with({'a': 'b'})
    case_of_default.compile.assert_has_calls([
        call({}),
        call({'k': 'v'})],
    )
    case_of_default.of_default.assert_called_once_with({'c': 'd'})
    sub_case.compile.assert_called_once_with({'sub_k': 'sub_v'})
