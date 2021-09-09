"""Context definitions."""

from contextlib import contextmanager
from typing import Dict, Iterator

Context = Dict[str, object]

CONTEXT_KEY_STARTS = "starts"
CONTEXT_KEY_BASE_URL = "base_url"


@contextmanager
def closed_context(context: Context, **kwargs) -> Iterator[Context]:
    stored = {key: context[key] for key in kwargs if key in context}

    context.update(kwargs)
    yield context

    for key in kwargs:
        if key in stored:
            context[key] = stored[key]
        else:
            if key in context:
                del context[key]
