from unittest.mock import MagicMock, call, patch, sentinel

from pytest import mark, raises, fixture

from preacher.compilation.argument import ArgumentValue
from preacher.compilation.case import CaseCompiler
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.scenario import ScenarioCompiler

PACKAGE = 'preacher.compilation.scenario'
ctor_patch = patch(f'{PACKAGE}.Scenario', return_value=sentinel.scenario)
compile_parameter_patch = patch(f'{PACKAGE}.compile_parameter')


@fixture
def compiler(description, case):
    return ScenarioCompiler(description, case)


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
    ({'parameters': ''}, [NamedNode('parameters')]),
    ({'parameters': {}}, [NamedNode('parameters')]),
    ({'cases': ''}, [NamedNode('cases')]),
    ({'subscenarios': ''}, [NamedNode('subscenarios')]),
    ({'default': ''}, [NamedNode('default')]),
))
def test_when_given_invalid_values(value, expected_path, compiler):
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert error_info.value.path == expected_path


@ctor_patch
def test_given_an_empty_object(ctor, compiler, case):
    scenario = compiler.compile({})

    assert scenario is sentinel.scenario
    ctor.assert_called_once_with(
        label=None,
        conditions=[],
        cases=[],
        subscenarios=[],
    )

    case.of_default.assert_called_once_with({})


@ctor_patch
def test_given_a_filled_object(
    ctor,
    compiler,
    description,
    case,
    case_of_default,
    sub_case
):
    scenario = compiler.compile(
        obj={
            'label': ArgumentValue('arg1'),
            'default': {'a': ArgumentValue('arg2')},
            'when': {'b': ArgumentValue('arg3')},
            'cases': [{}, {'c': ArgumentValue('arg4')}],
            'subscenarios': [
                {
                    'label': ArgumentValue('arg5'),
                    'default': {'d': ArgumentValue('arg6')},
                    'cases': [{'e': ArgumentValue('arg7')}]
                },
            ],
        },
        arguments={f'arg{i}': f'v{i}' for i in range(1, 8)},
    )
    assert scenario is sentinel.scenario

    ctor.assert_has_calls([
        call(
            label='v5',
            conditions=[],
            cases=[sentinel.sub_case],
            subscenarios=[],
        ),
        call(
            label='v1',
            conditions=[sentinel.description],
            cases=[sentinel.case, sentinel.case],
            subscenarios=[sentinel.scenario],
        ),
    ])
    description.compile.assert_called_once_with({'b': 'v3'})
    case.of_default.assert_called_once_with({'a': 'v2'})
    case_of_default.compile.assert_has_calls([
        call({}),
        call({'c': 'v4'}),
    ])
    case_of_default.of_default.assert_called_once_with({'d': 'v6'})
    sub_case.compile.assert_called_once_with({'e': 'v7'})


@compile_parameter_patch
@ctor_patch
def test_given_empty_parameter(ctor, compile_parameter, compiler):
    scenario = compiler.compile({'parameters': []})
    assert scenario is sentinel.scenario

    ctor.assert_called_once_with(label=None, subscenarios=[])
    compile_parameter.assert_not_called()
