from pluggy.hooks import HookspecMarker

hookspec = HookspecMarker('preacher')


@hookspec
def preacher_add_matchers(compiler) -> None:
    """
    Add Hamcrest matchers to a compiler.

    Args:
        compiler: A compiler to modify.
    """
