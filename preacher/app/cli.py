"""Preacher CLI."""

import argparse
import logging
import sys

import ruamel.yaml as yaml

from preacher import __version__ as VERSION
from preacher.core.scenario import ResponseScenario
from preacher.core.compilation import compile_response_scenario
from .view import LoggingView


LOGGER = logging.getLogger(__name__)


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
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    parser.add_argument('conf', nargs='+')

    return parser.parse_args()


def main() -> None:
    """Main."""
    args = parse_args()
    config_paths = args.conf

    view = LoggingView(LOGGER)
    app = Application(view)

    for config_path in config_paths:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
        scenario = compile_response_scenario(config)
        app.consume_scenario(scenario)

    if not app.is_succeeded:
        sys.exit(1)
