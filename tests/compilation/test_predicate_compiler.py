from unittest.mock import patch, sentinel

from preacher.compilation.predicate import PredicateCompiler


PACKAGE = 'preacher.compilation.predicate'


@patch(f'{PACKAGE}.compile_matcher', return_value=sentinel.compile_matcher)
def test_foo(matcher):
    compiler = PredicateCompiler()
    compiler.compile('matcher')
    matcher.assert_called_with('matcher')
