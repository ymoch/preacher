from datetime import datetime, timezone

import hamcrest

from preacher.compilation.datetime import compile_timedelta
from preacher.core.datetime import DatetimeWithFormat
from preacher.core.value import Value, StaticValue, RelativeDatetime
from preacher.core.verification import require_type, StaticMatcherFactory
from preacher.core.verification.hamcrest import before, after
from preacher.plugin import hookimpl
from .compiler import MatcherFactoryCompiler


@hookimpl
def preacher_add_matchers(compiler: MatcherFactoryCompiler) -> None:
    """
    Add default matchers to a compiler.

    Args:
        compiler: A compiler to be modified.
    """

    compiler.add_recursive(('be',), hamcrest.is_, multiple=False)

    # For objects.
    compiler.add_static(('be_null',), hamcrest.none())
    compiler.add_static(('not_be_null',), hamcrest.not_none())
    compiler.add_taking_value(('equal',), hamcrest.equal_to)
    compiler.add_recursive(('have_length',), hamcrest.has_length, multiple=False)

    # For comparable values.
    compiler.add_taking_value(('be_greater_than',), hamcrest.greater_than)
    compiler.add_taking_value(('be_greater_than_or_equal_to',), hamcrest.greater_than_or_equal_to)
    compiler.add_taking_value(('be_less_than',), hamcrest.less_than)
    compiler.add_taking_value(('be_less_than_or_equal_to',), hamcrest.less_than_or_equal_to)

    # For strings.
    compiler.add_taking_value(('contain_string',), require_type(str, hamcrest.contains_string))
    compiler.add_taking_value(('start_with',), require_type(str, hamcrest.starts_with))
    compiler.add_taking_value(('end_with',), require_type(str, hamcrest.ends_with))
    compiler.add_taking_value(('match_regexp',), require_type(str, hamcrest.matches_regexp))

    # For collections.
    compiler.add_recursive(('have_item',), hamcrest.has_item, multiple=False)
    compiler.add_recursive(('have_items',), hamcrest.has_items)
    compiler.add_recursive(('contain',), hamcrest.contains_exactly)  # HACK should be deprecated.
    compiler.add_recursive(('contain_exactly',), hamcrest.contains_exactly)
    compiler.add_recursive(('contain_in_any_order',), hamcrest.contains_inanyorder)

    # For datetime.
    compiler.add_taking_value(('be_before',), before, _compile_datetime_value)
    compiler.add_taking_value(('be_after',), after, _compile_datetime_value)

    # For collections.
    compiler.add_static(('be_empty',), StaticMatcherFactory(hamcrest.empty()))

    # Logical.
    compiler.add_static('anything', StaticMatcherFactory(hamcrest.anything()))
    compiler.add_recursive(('not',), hamcrest.not_, multiple=False)
    compiler.add_recursive(('all_of',), hamcrest.all_of)
    compiler.add_recursive(('any_of',), hamcrest.any_of)


def _compile_datetime_value(value: object) -> Value[DatetimeWithFormat]:
    if isinstance(value, datetime):
        if not value.tzinfo:
            value = value.replace(tzinfo=timezone.utc)
        return StaticValue(DatetimeWithFormat(value))

    delta = compile_timedelta(value)
    return RelativeDatetime(delta)
