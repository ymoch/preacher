from preacher.compilation.yaml.loader import Loader
from .argument import ArgumentTag
from .inclusion import InclusionTag

__all__ = ["add_default_tags"]


def add_default_tags(loader: Loader) -> None:
    loader.add_tag_constructor("!include", InclusionTag())
    loader.add_tag_constructor("!argument", ArgumentTag())
