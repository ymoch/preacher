from pluggy.hooks import HookspecMarker

from preacher.compilation.verification.matcher import MatcherFactoryCompiler

hookspec = HookspecMarker('preacher')


@hookspec
def preacher_add_matchers(compiler: MatcherFactoryCompiler) -> None:
    """
    Add Hamcrest matchers to a compiler.

    Args:
        compiler: A compiler to modify.
    """
