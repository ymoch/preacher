from unittest.mock import MagicMock, call, patch, sentinel

from pytest import mark, raises, fixture

from preacher.compilation.case import CaseCompiler
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.scenario import ScenarioCompiler


CONSTRUCTOR = 'preacher.compilation.scenario.Scenario'


@fixture
def description_compiler():
    return MagicMock(spec=DescriptionCompiler)


@fixture
def case_compiler():
    return MagicMock(spec=CaseCompiler)


@mark.parametrize('value, expected_path', (
    ('', []),
    ({'label': []}, [NamedNode('label')]),
    ({'cases': ''}, [NamedNode('cases')]),
    ({'subscenarios': ''}, [NamedNode('subscenarios')]),
    ({'default': ''}, [NamedNode('default')]),
))
def test_when_given_invalid_values(
    value,
    expected_path,
    description_compiler,
    case_compiler
):
    with raises(CompilationError) as error_info:
        ScenarioCompiler(
            description=description_compiler,
            case=case_compiler,
        ).compile(value)
    assert error_info.value.path == expected_path


@patch(CONSTRUCTOR, return_value=sentinel.scenario)
def test_given_an_empty_object(ctor, description_compiler, case_compiler):
    compiler = ScenarioCompiler(
        description=description_compiler,
        case=case_compiler
    )
    scenario = compiler.compile({})

    assert scenario is sentinel.scenario
    ctor.assert_called_once_with(
        label=None,
        conditions=[],
        cases=[],
        subscenarios=[],
    )

    case_compiler.of_default.assert_called_once_with({})


@patch(CONSTRUCTOR, return_value=sentinel.scenario)
def test_given_a_filled_object(ctor):
    description_compiler = MagicMock(
        spec=DescriptionCompiler,
        compile=MagicMock(return_value=sentinel.desc),
    )
    sub_case_compiler = MagicMock(
        spec=CaseCompiler,
        compile=MagicMock(return_value=sentinel.sub_case),
    )
    default_case_compiler = MagicMock(
        spec=CaseCompiler,
        compile=MagicMock(return_value=sentinel.case),
        of_default=MagicMock(return_value=sub_case_compiler),
    )
    case_compiler = MagicMock(
        spec=CaseCompiler,
        of_default=MagicMock(return_value=default_case_compiler),
    )
    compiler = ScenarioCompiler(
        description=description_compiler,
        case=case_compiler,
    )
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
            conditions=[sentinel.desc],
            cases=[sentinel.case, sentinel.case],
            subscenarios=[sentinel.scenario],
        ),
    ])

    case_compiler.of_default.assert_called_once_with({'a': 'b'})
    default_case_compiler.compile.assert_has_calls([
        call({}),
        call({'k': 'v'})],
    )
    default_case_compiler.of_default.assert_called_once_with({'c': 'd'})
    sub_case_compiler.compile.assert_has_calls([
        call({'sub_k': 'sub_v'}),
    ])
