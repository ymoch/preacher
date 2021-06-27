from logging import Formatter
from typing import Optional

from preacher.core.scheduling import Listener, MergingListener
from preacher.core.status import Status
from .logging import create_logging_reporting_listener
from .html import create_html_reporting_listener


def create_listener(
    level: Status = Status.SUCCESS,
    formatter: Optional[Formatter] = None,
    report_dir: Optional[str] = None,
) -> Listener:
    merging = MergingListener()
    merging.append(create_logging_reporting_listener(level=level, formatter=formatter))
    if report_dir:
        merging.append(create_html_reporting_listener(report_dir))
    return merging
