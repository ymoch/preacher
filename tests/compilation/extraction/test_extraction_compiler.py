from typing import List, Tuple
from unittest.mock import Mock, call, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.extraction.extraction import ExtractionCompiler, add_default_extractions
from preacher.compilation.extraction.extraction import compile_jq, compile_xpath, compile_key
from preacher.core.extraction.impl.jq_engine import PyJqEngine

PKG = "preacher.compilation.extraction.extraction"


@fixture
def jq_factory():
    return Mock(return_value=sentinel.jq)


@fixture
def xpath_factory():
    return Mock(return_value=sentinel.xpath)


@fixture
def compiler(jq_factory, xpath_factory):
    compiler = ExtractionCompiler()
    compiler.add_factory("jq", jq_factory)
    compiler.add_factory("xpath", xpath_factory)
    return compiler


@mark.parametrize(
    "value, expected_message, expected_path",
    (
        (1, "", []),
        ([], "", []),
        ({}, " has 0", []),
        ({"jq": ".foo", "xpath": "bar"}, "has 2", []),
    ),
)
def test_when_given_invalid_value(compiler, value, expected_message, expected_path):
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert expected_message in str(error_info.value)
    assert error_info.value.path == expected_path


def test_when_given_a_string(compiler, jq_factory, xpath_factory):
    assert compiler.compile(".foo") is sentinel.jq
    jq_factory.assert_called_once_with(".foo", {"jq": ".foo"})
    xpath_factory.assert_not_called()


def test_when_given_a_jq_object(compiler, jq_factory, xpath_factory):
    assert compiler.compile({"jq": ".foo", "spam": "ham"}) is sentinel.jq
    jq_factory.assert_called_once_with(".foo", {"jq": ".foo", "spam": "ham"})
    xpath_factory.assert_not_called()


def test_when_given_an_xpath_object(compiler, jq_factory, xpath_factory):
    assert compiler.compile({"xpath": "/foo", "spam": "ham"}) is sentinel.xpath
    jq_factory.assert_not_called()
    xpath_factory.assert_called_once_with("/foo", {"xpath": "/foo", "spam": "ham"})


if PyJqEngine.is_available():

    @mark.parametrize(
        ("value", "expected_message", "expected_path"),
        (
            ({"multiple": 1}, "", [NamedNode("multiple")]),
            ({"cast_to": 1}, " string", [NamedNode("cast_to")]),
            ({"cast_to": "xxx"}, ": xxx", [NamedNode("cast_to")]),
        ),
    )
    def test_compile_jq_when_given_invalid_options(value, expected_message, expected_path):
        with raises(CompilationError) as error_info:
            compile_jq(".xxx", value)
        assert expected_message in str(error_info.value)
        assert error_info.value.path == expected_path

    @mark.parametrize(
        ("query", "options", "expected_call"),
        (
            (".foo", {}, call(sentinel.engine, ".foo", multiple=False, cast=None)),
            (
                ".bar",
                {"multiple": True, "cast_to": "int"},
                call(sentinel.engine, ".bar", multiple=True, cast=int),
            ),
        ),
    )
    def test_compile_jq(mocker, query, options, expected_call):
        engine_ctor = mocker.patch(f"{PKG}.PyJqEngine", return_value=sentinel.engine)
        factory = mocker.patch(f"{PKG}.JqExtractor", return_value=sentinel.extraction)

        assert compile_jq(query, options) is sentinel.extraction
        engine_ctor.assert_called_once_with()
        factory.assert_has_calls([expected_call])


@mark.parametrize(
    ("value", "expected_message", "expected_path"),
    (
        ({"multiple": 1}, "", [NamedNode("multiple")]),
        ({"cast_to": 1}, " string", [NamedNode("cast_to")]),
        ({"cast_to": "xxx"}, ": xxx", [NamedNode("cast_to")]),
    ),
)
def test_compile_xpath_when_given_invalid_options(value, expected_message, expected_path):
    with raises(CompilationError) as error_info:
        compile_xpath("./xxx", value)
    assert expected_message in str(error_info.value)
    assert error_info.value.path == expected_path


@mark.parametrize(
    ("query", "options", "expected_call"),
    (
        (".foo", {}, call(".foo", multiple=False, cast=None)),
        ("/bar", {"multiple": True, "cast_to": "int"}, call("/bar", multiple=True, cast=int)),
    ),
)
def test_compile_xpath(mocker, query, options, expected_call):
    factory = mocker.patch(f"{PKG}.XPathExtractor", return_value=sentinel.extraction)

    assert compile_xpath(query, options) is sentinel.extraction
    factory.assert_has_calls([expected_call])


@mark.parametrize(
    ("value", "expected_message", "expected_path"),
    (
        ({"multiple": 1}, "", [NamedNode("multiple")]),
        ({"cast_to": 1}, " string", [NamedNode("cast_to")]),
        ({"cast_to": "xxx"}, ": xxx", [NamedNode("cast_to")]),
    ),
)
def test_compile_key_when_given_invalid_options(value, expected_message, expected_path):
    with raises(CompilationError) as error_info:
        compile_key("xxx", value)
    assert expected_message in str(error_info.value)
    assert error_info.value.path == expected_path


@mark.parametrize(
    ("query", "options", "expected_call"),
    (
        ("foo", {}, call("foo", multiple=False, cast=None)),
        ("bar", {"multiple": True, "cast_to": "float"}, call("bar", multiple=True, cast=float)),
    ),
)
def test_compile_key(mocker, query, options, expected_call):
    factory = mocker.patch(f"{PKG}.KeyExtractor", return_value=sentinel.extraction)

    assert compile_key(query, options) is sentinel.extraction
    factory.assert_has_calls([expected_call])


ADD_DEFAULT_EXTRACTIONS_CASES: List[Tuple[object, str, object]] = [
    ({"xpath": "/foo"}, "XPathExtractor", call("/foo", multiple=False, cast=None)),
    ({"key": "foo"}, "KeyExtractor", call("foo", multiple=False, cast=None)),
]
if PyJqEngine.is_available():
    ADD_DEFAULT_EXTRACTIONS_CASES.append(
        (".foo", "JqExtractor", call(sentinel.engine, ".foo", multiple=False, cast=None))
    )
    ADD_DEFAULT_EXTRACTIONS_CASES.append(
        (
            {"jq": ".foo"},
            "JqExtractor",
            call(sentinel.engine, ".foo", multiple=False, cast=None),
        )
    )


@mark.parametrize(
    ("value", "expected_factory", "expected_call"),
    ADD_DEFAULT_EXTRACTIONS_CASES,
)
def test_add_default_extractions(mocker, value, expected_factory, expected_call):
    compiler = ExtractionCompiler()
    add_default_extractions(compiler)

    factory = mocker.patch(f"{PKG}.{expected_factory}", return_value=sentinel.extraction)
    mocker.patch(f"{PKG}.PyJqEngine", return_value=sentinel.engine)

    assert compiler.compile(value) is sentinel.extraction
    factory.assert_has_calls([expected_call])
