from pluggy import HookspecMarker
from yamlen import Loader

from preacher.compilation.extraction import ExtractionCompiler
from preacher.compilation.verification.matcher import MatcherFactoryCompiler

hookspec = HookspecMarker("preacher")


@hookspec
def preacher_add_matchers(compiler: MatcherFactoryCompiler) -> None:
    """
    Add Hamcrest matchers to a compiler.

    Args:
        compiler: A compiler to modify.
    """


@hookspec
def preacher_add_extractions(compiler: ExtractionCompiler) -> None:
    """
    Add extractions to a compiler

    Args:
        compiler: A compiler to modify.
    """


@hookspec
def preacher_modify_yaml_loader(loader: Loader) -> None:
    """
    Modify a YAML loader.

    Args:
        loader: A loader to be modified.
    """
