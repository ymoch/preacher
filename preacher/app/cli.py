"""Preacher CLI."""

import argparse
import logging
import sys

import ruamel.yaml as yaml

from preacher import __version__ as VERSION
from preacher.core.scenario import ResponseScenario
from preacher.compilation.scenario import compile_response_scenario
from .view import LoggingView


HANDLER = logging.StreamHandler()
HANDLER.setLevel(logging.WARN)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)


class Application:
    def __init__(self, view: LoggingView) -> None:
        self._view = view
        self._is_succeeded = True

    @property
    def is_succeeded(self) -> bool:
        return self._is_succeeded

    def consume_scenario(self, scenario: ResponseScenario) -> None:
        data = b'{"foo": "bar"}'
        verification = scenario(body=data)

        self._is_succeeded &= verification.status.is_succeeded
        self._view.show_response_verification(verification, 'Response')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'conf',
        nargs='+',
        help='confign file paths'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=VERSION,
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
    config_paths = args.conf
    should_be_quiet = args.quiet

    logging_level = logging.INFO
    if should_be_quiet:
        logging_level = logging.WARN
    HANDLER.setLevel(logging_level)

    view = LoggingView(LOGGER)
    app = Application(view)

    for config_path in config_paths:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
        scenario = compile_response_scenario(config)
        app.consume_scenario(scenario)

    if not app.is_succeeded:
        sys.exit(1)
