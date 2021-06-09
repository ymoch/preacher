from preacher.compilation.yaml.loader import Loader
from .argument import ArgumentTag
from .datetime import RelativeDatetimeTag
from .inclusion import InclusionTag

__all__ = ["add_default_tags"]


def add_default_tags(loader: Loader) -> None:
    loader.add_tag("!argument", ArgumentTag())
    loader.add_tag("!include", InclusionTag())
    loader.add_tag("!relative_datetime", RelativeDatetimeTag())
