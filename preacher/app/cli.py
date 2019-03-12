"""Preacher CLI."""

import argparse
import sys

from preacher import __version__ as VERSION
from preacher.core.compilation import compile_description


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    return parser.parse_args()


def main() -> None:
    """Main."""
    parse_args()

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
