from unittest.mock import Mock, NonCallableMock, call, sentinel

from pytest import mark, raises, fixture

from preacher.compilation.argument import ArgumentValue
from preacher.compilation.error import CompilationError, NamedNode, IndexedNode
from preacher.compilation.parameter import Parameter
from preacher.compilation.scenario.case import CaseCompiler
from preacher.compilation.scenario.scenario import ScenarioCompiler
from preacher.compilation.verification import DescriptionCompiler

PKG = 'preacher.compilation.scenario.scenario'


@fixture
def compiler(description, case) -> ScenarioCompiler:
    return ScenarioCompiler(description=description, case=case)


@fixture
def description():
    compiler = NonCallableMock(DescriptionCompiler)
    compiler.compile.return_value = sentinel.description
    return compiler


@fixture
def case(case_of_default):
    compiler = NonCallableMock(CaseCompiler)
    compiler.compile_default = Mock(return_value=case_of_default)
    return compiler


@fixture
def case_of_default(sub_case):
    compiler = NonCallableMock(CaseCompiler)
    compiler.compile_fixed.return_value = sentinel.case
    compiler.compile_default = Mock(return_value=sub_case)
    return compiler


@fixture
def sub_case():
    compiler = NonCallableMock(CaseCompiler)
    compiler.compile_fixed.return_value = sentinel.sub_case
    return compiler


@mark.parametrize('value, expected_path', (
    ('', []),
    ({'label': []}, [NamedNode('label')]),
    ({'ordered': 1}, [NamedNode('ordered')]),
    ({'parameters': ''}, [NamedNode('parameters'), IndexedNode(0)]),
    ({'subscenarios': ''}, [NamedNode('subscenarios'), IndexedNode(0)]),
))
def test_when_given_invalid_values(value, expected_path, compiler):
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert error_info.value.path == expected_path


def test_given_an_empty_object(
    compiler: ScenarioCompiler,
    case,
    case_of_default,
    mocker,
):
    ctor = mocker.patch(f'{PKG}.Scenario', return_value=sentinel.scenario)

    scenario = compiler.compile({})

    assert scenario is sentinel.scenario
    ctor.assert_called_once_with(
        label=None,
        ordered=True,
        conditions=[],
        cases=[],
        subscenarios=[],
    )

    case.compile_default.assert_called_once_with({})
    case_of_default.compile_fixed.assert_not_called()


def test_given_a_filled_object(
    compiler: ScenarioCompiler,
    description,
    case,
    case_of_default,
    sub_case,
    mocker,
):
    ctor = mocker.patch(f'{PKG}.Scenario', return_value=sentinel.scenario)

    scenario = compiler.compile(
        obj={
            'label': ArgumentValue('arg1'),
            'ordered': False,
            'default': {'a': ArgumentValue('arg2')},
            'when': {'b': ArgumentValue('arg3')},
            'cases': [{}, {'c': ArgumentValue('arg4')}],
            'subscenarios': [
                {
                    'label': ArgumentValue('arg5'),
                    'ordered': True,
                    'default': {'d': ArgumentValue('arg6')},
                    'cases': [{'e': ArgumentValue('arg7')}]
                },
            ],
        },
        arguments={f'arg{i}': f'v{i}' for i in range(1, 9)},
    )
    assert scenario is sentinel.scenario

    ctor.assert_has_calls([
        call(
            label='v5',
            ordered=True,
            conditions=[],
            cases=[sentinel.sub_case],
            subscenarios=[],
        ),
        call(
            label='v1',
            ordered=False,
            conditions=[sentinel.description],
            cases=[sentinel.case, sentinel.case],
            subscenarios=[sentinel.scenario],
        ),
    ])
    description.compile.assert_called_once_with({'b': 'v3'})
    case.compile_default.assert_called_once_with({'a': 'v2'})
    case_of_default.compile_fixed.assert_has_calls([
        call({}),
        call({'c': 'v4'}),
    ])
    case_of_default.compile_default.assert_called_once_with({'d': 'v6'})
    sub_case.compile_fixed.assert_called_once_with({'e': 'v7'})


def test_given_empty_parameter(compiler: ScenarioCompiler, mocker):
    ctor = mocker.patch(f'{PKG}.Scenario', return_value=sentinel.scenario)
    compile_parameter = mocker.patch(f'{PKG}.compile_parameter')

    scenario = compiler.compile({'parameters': []})
    assert scenario is sentinel.scenario

    ctor.assert_called_once_with(label=None, subscenarios=[])
    compile_parameter.assert_not_called()


def test_when_parameter_compilation_fails(compiler: ScenarioCompiler, mocker):
    compile_parameter = mocker.patch(f'{PKG}.compile_parameter')
    compile_parameter.side_effect = CompilationError('message')

    with raises(CompilationError) as error_info:
        compiler.compile({'parameters': [sentinel.param_obj]})
    assert error_info.value.path == [NamedNode('parameters'), IndexedNode(0)]

    compile_parameter.assert_called_once_with(sentinel.param_obj)


def test_given_filled_parameters(
    compiler: ScenarioCompiler,
    description,
    case,
    case_of_default,
    mocker,
):
    ctor = mocker.patch(f'{PKG}.Scenario', return_value=sentinel.scenario)
    compile_parameter = mocker.patch(f'{PKG}.compile_parameter')
    compile_parameter.side_effect = [
        Parameter(
            label='param1',
            arguments={'foo': 'bar', 'ordered': False},
        ),
        Parameter(
            label='param2',
            arguments={'foo': 'baz', 'spam': 'eggs', 'ordered': True},
        ),
    ]

    scenario = compiler.compile(
        obj={
            'label': ArgumentValue('original_label'),
            'ordered': ArgumentValue('ordered'),
            'parameters': [sentinel.param_obj1, sentinel.param_obj2],
            'default': {'foo': ArgumentValue('foo')},
            'when': [{'foo': ArgumentValue('foo')}],
            'cases': [{'spam': ArgumentValue('spam')}],
            'subscenarios': [{'label': ArgumentValue('spam')}]
        },
        arguments={'original_label': 'original', 'spam': 'ham'},
    )
    assert scenario is sentinel.scenario

    ctor.assert_has_calls([
        call(
            label='ham',
            ordered=True,
            conditions=[],
            cases=[],
            subscenarios=[],
        ),
        call(
            label='param1',
            ordered=False,
            conditions=[sentinel.description],
            cases=[sentinel.case],
            subscenarios=[sentinel.scenario],
        ),
        call(
            label='eggs',
            ordered=True,
            conditions=[],
            cases=[],
            subscenarios=[],
        ),
        call(
            label='param2',
            ordered=True,
            conditions=[sentinel.description],
            cases=[sentinel.case],
            subscenarios=[sentinel.scenario],
        ),
        call(label='original', subscenarios=[sentinel.scenario] * 2)
    ])
    compile_parameter.assert_has_calls([
        call(sentinel.param_obj1),
        call(sentinel.param_obj2),
    ])
    description.compile.assert_has_calls([
        call({'foo': 'bar'}),
        call({'foo': 'baz'}),
    ])
    case.compile_default.assert_has_calls([
        call({'foo': 'bar'}),
        call({'foo': 'baz'}),
    ])
    case_of_default.compile_fixed.assert_has_calls([
        call({'spam': 'ham'}),
        call({'spam': 'eggs'}),
    ])
    case_of_default.compile_default.assert_has_calls([
        call().compile_default({}),
        call().compile_default({}),
    ])


def test_compile_flattening(compiler: ScenarioCompiler):
    obj = [
        [],
        [
            [{'label': 'foo'}],
            {'label': ArgumentValue('arg')},
            [[{'label': 1}]]
        ],
    ]

    scenarios = compiler.compile_flattening(obj, {'arg': 'bar'})
    assert next(scenarios).label == 'foo'
    assert next(scenarios).label == 'bar'

    with raises(CompilationError) as error_info:
        next(scenarios)
    assert error_info.value.path == [
        IndexedNode(1),
        IndexedNode(2),
        IndexedNode(0),
        IndexedNode(0),
        NamedNode('label'),
    ]

    with raises(StopIteration):
        next(scenarios)
