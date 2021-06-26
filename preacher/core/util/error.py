"""Error handling utilities."""


def to_message(error: Exception) -> str:
    return f"{error.__class__.__name__}: {error}"
