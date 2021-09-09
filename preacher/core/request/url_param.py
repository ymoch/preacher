"""URL Parameters."""

from datetime import date
from typing import Union, List, Mapping, Optional

from preacher.core.context import Context
from preacher.core.datetime import DatetimeWithFormat
from preacher.core.value import Value

UrlParam = Union[object, List[object]]
UrlParams = Union[str, Mapping[str, UrlParam]]
ResolvedUrlParamValue = Optional[str]
ResolvedUrlParam = Union[ResolvedUrlParamValue, List[ResolvedUrlParamValue]]
ResolvedUrlParams = Union[str, Mapping[str, ResolvedUrlParam]]


def resolve_url_param_value(value: object, context: Optional[Context] = None) -> Optional[str]:
    """
    Resolve a URL parameter value.

    Args:
        value: A URL parameter value.
        context: A resolution context.
    Returns:
        The resolved value.
    Raises:
        ValueError: when given a not resolvable value.
    """
    if isinstance(value, Value):
        value = value.resolve(context)

    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, DatetimeWithFormat):
        return value.formatted
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def resolve_url_param(param: UrlParam, context: Optional[Context] = None) -> ResolvedUrlParam:
    if isinstance(param, list):
        return [resolve_url_param_value(value, context) for value in param]
    return resolve_url_param_value(param, context)


def resolve_url_params(params: UrlParams, context: Optional[Context] = None) -> ResolvedUrlParams:
    if isinstance(params, str):
        return params
    return {key: resolve_url_param(param, context) for (key, param) in params.items()}
