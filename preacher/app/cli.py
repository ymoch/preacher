"""Preacher CLI."""

import sys

from preacher.core.compilation import compile_description


def main() -> None:
    """Main."""
    description = compile_description({
        'jq': '.foo',
        'it': {
            'equals_to': 'bar',
        },
    })
    data = {'foo': 'bar'}
    verification = description.verify(data)
    if not verification.is_valid:
        sys.exit(1)
