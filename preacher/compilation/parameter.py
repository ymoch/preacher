from dataclasses import dataclass, field
from typing import Optional

from .argument import Arguments
from .util import compile_mapping, compile_optional_str

_KEY_LABEL = 'label'
_KEY_ARGUMENTS = 'arguments'


@dataclass(frozen=True)
class Parameter:
    label: Optional[str] = None
    arguments: Arguments = field(default_factory=dict)


def compile(obj: object) -> Parameter:
    """
    Compile a parameter.

    Args:
        obj: A compiled object.
    Returns:
        A parameter as the result of compilation.
    Raises:
        CompilationError: when the compilation fails.
    """
    obj = compile_mapping(obj)
    label = compile_optional_str(obj.get(_KEY_LABEL))
    arguments = compile_mapping(obj.get(_KEY_ARGUMENTS, {}))
    return Parameter(label=label, arguments=arguments)
