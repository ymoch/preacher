from yamlen import Loader

from preacher.compilation.extraction.extraction import ExtractionCompiler, add_default_extractions
from preacher.compilation.verification.matcher import MatcherFactoryCompiler
from preacher.compilation.verification.matcher import add_default_matchers
from preacher.compilation.yaml.tag import add_default_tags
from . import hookimpl


@hookimpl(tryfirst=True)
def preacher_add_matchers(compiler: MatcherFactoryCompiler) -> None:
    add_default_matchers(compiler)


@hookimpl(tryfirst=True)
def preacher_add_extractions(compiler: ExtractionCompiler) -> None:
    add_default_extractions(compiler)


@hookimpl(tryfirst=True)
def preacher_modify_yaml_loader(loader: Loader) -> None:
    add_default_tags(loader)
