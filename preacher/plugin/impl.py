from . import hookimpl
from preacher.compilation.verification.matcher import MatcherFactoryCompiler
from preacher.compilation.verification.matcher import add_default_matchers


@hookimpl(tryfirst=True)
def preacher_add_matchers(compiler: MatcherFactoryCompiler) -> None:
    add_default_matchers(compiler)
