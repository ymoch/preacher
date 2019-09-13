from unittest.mock import MagicMock, call, sentinel

from pytest import fixture, mark

from preacher.compilation.body_description import BodyDescriptionCompiler
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError


@fixture
def desc_compiler():
    return MagicMock(
        spec=DescriptionCompiler,
        compile=MagicMock(return_value=sentinel.desc),
    )


@mark.xfail(raises=CompilationError)
@mark.parametrize('value', (None, 0, ''))
def test_given_invalid_values(value):
    BodyDescriptionCompiler().compile(value)


@mark.parametrize('value', ({}, []))
def test_given_empty_values(value, desc_compiler):
    compiler = BodyDescriptionCompiler(description_compiler=desc_compiler)
    desc = compiler.compile({})
    assert desc.descriptions == []

    desc_compiler.compile.assert_not_called()


def test_given_an_mapping(desc_compiler):
    compiler = BodyDescriptionCompiler(description_compiler=desc_compiler)
    desc = compiler.compile({'descriptions': ['d1', 'd2']})
    assert desc.descriptions == [sentinel.desc, sentinel.desc]

    desc_compiler.compile.assert_has_calls([call('d1'), call('d2')])
