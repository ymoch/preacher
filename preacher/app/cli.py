"""Preacher CLI."""

import argparse
import functools
import os
import sys

import yaml

from preacher import __version__ as VERSION
from preacher.core.compilation import compile_description
from preacher.core.verification import Status, Verification


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('conf', nargs='+')

    return parser.parse_args()


def process_by_config(config_path: os.PathLike) -> Verification:
    with open(config_path) as config_file:
        config = yaml.load(config_file)
    description = compile_description(config)
    data = {'foo': 'bar'}
    return description(data)


def main() -> None:
    """Main."""
    args = parse_args()
    config_paths = args.conf

    verifications = (process_by_config(path) for path in config_paths)
    status = functools.reduce(
        lambda a, b: a.merge(b.status),
        verifications,
        Status.SUCCESS,
    )
    if not status.is_succeeded:
        sys.exit(1)
