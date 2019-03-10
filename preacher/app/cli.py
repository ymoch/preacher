"""Preacher CLI."""

import sys

from preacher.core.extraction import extraction_with_jq
from preacher.core.description import Description
from preacher.core.predicate import equal_to


def main() -> None:
    """Main."""
    description = Description(
        extraction=extraction_with_jq('.foo'),
        predicates=[equal_to('bar')],
    )
    data = {'foo': 'bar'}
    verification = description.verify(data)
    if not verification.is_valid:
        sys.exit(1)
