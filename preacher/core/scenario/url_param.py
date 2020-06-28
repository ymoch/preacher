from datetime import date, datetime
from typing import Union, List, Mapping, Optional

from preacher.core.interpretation.value import Value

UrlParamValue = Union[
    None,
    bool,
    int,
    float,
    str,
    date,
    datetime,
    Value[None],
    Value[bool],
    Value[int],
    Value[float],
    Value[str],
    Value[datetime],
]
UrlParam = Union[UrlParamValue, List[UrlParamValue]]
UrlParams = Union[str, Mapping[str, UrlParam]]
ResolvedUrlParamValue = Optional[str]
ResolvedUrlParam = Union[ResolvedUrlParamValue, List[ResolvedUrlParamValue]]
ResolvedUrlParams = Union[str, Mapping[str, ResolvedUrlParam]]


def resolve_url_param_value(value: UrlParamValue, **kwargs) -> Optional[str]:
    if isinstance(value, Value):
        value = value.apply_context(**kwargs)

    if value is None:
        return None
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def resolve_url_param(param: UrlParam, **kwargs) -> ResolvedUrlParam:
    if isinstance(param, list):
        return [resolve_url_param_value(value, **kwargs) for value in param]
    return resolve_url_param_value(param)


def resolve_url_params(params: UrlParams, **kwargs) -> ResolvedUrlParams:
    if isinstance(params, str):
        return params
    return {
        key: resolve_url_param(param, **kwargs)
        for (key, param) in params.items()
    }
