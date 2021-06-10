import logging
from io import StringIO

from colorama import Fore, Style
from pytest import mark

from preacher.app.cli.logging import ColoredFormatter, create_system_logger


def test_colored_formatter():
    formatter = ColoredFormatter()
    stream = StringIO()

    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    logger.debug('skipped')
    logger.info('success')
    logger.warning('unstable')
    logger.error('failure')
    logger.critical('critical')

    stream.seek(0)
    assert next(stream) == 'skipped\n'
    assert next(stream) == f'{Fore.GREEN}success{Style.RESET_ALL}\n'
    assert next(stream) == f'{Fore.YELLOW}unstable{Style.RESET_ALL}\n'
    assert next(stream) == f'{Fore.RED}failure{Style.RESET_ALL}\n'
    assert next(stream) == f'{Fore.RED}{Style.BRIGHT}critical{Style.RESET_ALL}\n'


@mark.parametrize(('verbosity', 'expected_level'), (
    (0, logging.WARNING),
    (1, logging.INFO),
    (2, logging.DEBUG),
    (3, logging.DEBUG),
))
def test_create_system_logger(verbosity: int, expected_level: int):
    logger = create_system_logger(verbosity=verbosity)
    assert logger.getEffectiveLevel() == expected_level
