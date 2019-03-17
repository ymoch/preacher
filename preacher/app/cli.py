"""Preacher CLI."""

from __future__ import annotations

import argparse
import logging
import sys

import ruamel.yaml as yaml

from preacher import __version__ as VERSION
from preacher.core.scenario import Scenario
from preacher.compilation.scenario import compile_scenario
from .view import LoggingView


HANDLER = logging.StreamHandler()
HANDLER.setLevel(logging.WARN)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)


class Application:
    def __init__(
        self: Application,
        base_url: str,
        view: LoggingView,
    ) -> None:
        self._view = view
        self._base_url = base_url
        self._is_succeeded = True

    @property
    def is_succeeded(self: Application) -> bool:
        return self._is_succeeded

    def consume_scenario(self: Application, scenario: Scenario) -> None:
        verification = scenario(base_url=self._base_url)

        self._is_succeeded &= verification.status.is_succeeded
        self._view.show_scenario_verification(verification, 'Response')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'conf',
        nargs='+',
        help='config file paths'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=VERSION,
    )
    parser.add_argument(
        '-u', '--url',
        metavar='url',
        help='specify the base URL',
        default='http://localhost:5000',
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='show details on the console only when an any issue occurs',
    )

    return parser.parse_args()


def main() -> None:
    """Main."""
    args = parse_args()

    logging_level = logging.INFO
    should_be_quiet = args.quiet
    if should_be_quiet:
        logging_level = logging.WARN
    HANDLER.setLevel(logging_level)

    base_url = args.url
    view = LoggingView(LOGGER)
    app = Application(base_url=base_url, view=view)

    config_paths = args.conf
    for config_path in config_paths:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
        scenario = compile_scenario(config)
        app.consume_scenario(scenario)

    if not app.is_succeeded:
        sys.exit(1)
