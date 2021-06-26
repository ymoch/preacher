"""URL Parameters."""

from datetime import date, datetime
from typing import Union, List, Mapping, Optional

from preacher.core.datetime import DatetimeWithFormat
from preacher.core.value import Value, ValueContext

UrlParamValue = Union[
    None,
    bool,
    int,
    float,
    str,
    date,
    datetime,
    DatetimeWithFormat,
    Value[None],
    Value[bool],
    Value[int],
    Value[float],
    Value[str],
    Value[date],
    Value[datetime],
    Value[DatetimeWithFormat],
]
UrlParam = Union[UrlParamValue, List[UrlParamValue]]
UrlParams = Union[str, Mapping[str, UrlParam]]
ResolvedUrlParamValue = Optional[str]
ResolvedUrlParam = Union[ResolvedUrlParamValue, List[ResolvedUrlParamValue]]
ResolvedUrlParams = Union[str, Mapping[str, ResolvedUrlParam]]


def resolve_url_param_value(
    value: UrlParamValue,
    context: Optional[ValueContext] = None,
) -> Optional[str]:
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


def resolve_url_param(
    param: UrlParam,
    context: Optional[ValueContext] = None,
) -> ResolvedUrlParam:
    if isinstance(param, list):
        return [resolve_url_param_value(value, context) for value in param]
    return resolve_url_param_value(param)


def resolve_url_params(
    params: UrlParams,
    context: Optional[ValueContext] = None,
) -> ResolvedUrlParams:
    if isinstance(params, str):
        return params
    return {key: resolve_url_param(param, context) for (key, param) in params.items()}
