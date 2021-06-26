from dataclasses import dataclass, field
from typing import Optional

from .argument import Arguments
from .error import on_key
from .util.type import ensure_optional_str, ensure_mapping

_KEY_LABEL = "label"
_KEY_ARGUMENTS = "args"


@dataclass(frozen=True)
class Parameter:
    label: Optional[str] = None
    arguments: Arguments = field(default_factory=dict)


def compile_parameter(obj: object) -> Parameter:
    """
    Compile a parameter.

    Args:
        obj: A compiled object.
    Returns:
        A parameter as the result of compilation.
    Raises:
        CompilationError: when the compilation fails.
    """
    obj = ensure_mapping(obj)

    with on_key(_KEY_LABEL):
        label = ensure_optional_str(obj.get(_KEY_LABEL))
    with on_key(_KEY_ARGUMENTS):
        arguments = ensure_mapping(obj.get(_KEY_ARGUMENTS, {}))
    return Parameter(label=label, arguments=arguments)
