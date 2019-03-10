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
    verification = description(data)
    if not verification.status.is_succeeded:
        sys.exit(1)
