import logging
from io import StringIO

from colorama import Fore, Style

from preacher.app.cli.logging import ColoredFormatter


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
