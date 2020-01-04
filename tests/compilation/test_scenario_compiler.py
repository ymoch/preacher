from unittest.mock import MagicMock, call, patch, sentinel

from pytest import mark, raises, fixture

from preacher.compilation.argument import ArgumentValue
from preacher.compilation.case import CaseCompiler, CaseCompiled
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError, NamedNode, IndexedNode
from preacher.compilation.parameter import Parameter
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
    compiler.compile.return_value = sentinel.default
    compiler.of_default.return_value = case_of_default
    return compiler


@fixture
def case_of_default(case_compiled, sub_case):
    compiler = MagicMock(spec=CaseCompiler)
    compiler.compile.return_value = case_compiled
    compiler.of_default.return_value = sub_case
    return compiler


@fixture
def case_compiled():
    compiled = MagicMock(spec=CaseCompiled)
    compiled.fix.return_value = sentinel.case
    return compiled


@fixture
def sub_case(sub_case_compiled):
    compiler = MagicMock(spec=CaseCompiler)
    compiler.compile.return_value = sub_case_compiled
    return compiler


@fixture
def sub_case_compiled():
    compiled = MagicMock(spec=CaseCompiled)
    compiled.fix.return_value = sentinel.sub_case
    return compiled


@mark.parametrize('value, expected_path', (
    ('', []),
    ({'label': []}, [NamedNode('label')]),
    ({'parameters': ''}, [NamedNode('parameters')]),
    ({'parameters': {}}, [NamedNode('parameters')]),
    ({'cases': ''}, [NamedNode('cases')]),
    ({'subscenarios': ''}, [NamedNode('subscenarios')]),
))
def test_when_given_invalid_values(value, expected_path, compiler):
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert error_info.value.path == expected_path


@ctor_patch
def test_given_an_empty_object(
    ctor,
    compiler,
    case,
    case_of_default,
):
    scenario = compiler.compile({})

    assert scenario is sentinel.scenario
    ctor.assert_called_once_with(
        label=None,
        conditions=[],
        cases=[],
        subscenarios=[],
    )

    case.compile.assert_called_once_with({})
    case.of_default.assert_called_once_with(sentinel.default)
    case_of_default.compile.assert_not_called()


@ctor_patch
def test_given_a_filled_object(
    ctor,
    compiler,
    description,
    case,
    case_of_default,
    case_compiled,
    sub_case,
    sub_case_compiled,
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
    case.compile.assert_called_once_with({'a': 'v2'})
    case.of_default.assert_called_once_with(sentinel.default)
    case_of_default.compile.assert_has_calls([
        call({}),
        call().fix(),
        call({'c': 'v4'}),
        call().fix(),
        call({'d': 'v6'}),
    ])
    case_of_default.of_default.assert_called_once_with(case_compiled)
    sub_case.compile.assert_called_once_with({'e': 'v7'})
    sub_case_compiled.fix.assert_called_once_with()


@compile_parameter_patch
@ctor_patch
def test_given_empty_parameter(ctor, compile_parameter, compiler):
    scenario = compiler.compile({'parameters': []})
    assert scenario is sentinel.scenario

    ctor.assert_called_once_with(label=None, subscenarios=[])
    compile_parameter.assert_not_called()


@compile_parameter_patch
def test_when_parameter_compilation_fails(compile_parameter, compiler):
    compile_parameter.side_effect = CompilationError('message')
    with raises(CompilationError) as error_info:
        compiler.compile({'parameters': [sentinel.param_obj]})
    assert error_info.value.path == [NamedNode('parameters'), IndexedNode(0)]

    compile_parameter.assert_called_once_with(sentinel.param_obj)


@compile_parameter_patch
@ctor_patch
def test_given_filled_parameters(
    ctor,
    compile_parameter,
    compiler,
    description,
    case,
    case_compiled
):
    compile_parameter.side_effect = [
        Parameter(label='param1', arguments={'foo': 'bar'}),
        Parameter(label='param2', arguments={'foo': 'baz', 'spam': 'eggs'}),
    ]
    scenario = compiler.compile(
        obj={
            'label': ArgumentValue('original_label'),
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
        call(label='ham', conditions=[], cases=[], subscenarios=[]),
        call(
            label='param1',
            conditions=[sentinel.description],
            cases=[sentinel.case],
            subscenarios=[sentinel.scenario],
        ),
        call(label='eggs', conditions=[], cases=[], subscenarios=[]),
        call(
            label='param2',
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
    case.compile.assert_has_calls([
        call({'foo': 'bar'}),
        call({'foo': 'baz'}),
    ])
    case.of_default.assert_has_calls([
        call(sentinel.default),
        call().compile({'spam': 'ham'}),
        call().compile().fix(),
        call().compile({}),
        call().of_default(case_compiled),
        call(sentinel.default),
        call().compile({'spam': 'eggs'}),
        call().compile().fix(),
        call().compile({}),
        call().of_default(case_compiled),
    ])
