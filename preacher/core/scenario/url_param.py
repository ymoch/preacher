from datetime import datetime
from typing import Union, List, Mapping, Optional

from preacher.core.interpretation.value import Value

UrlParameterValue = Union[
    None,
    bool,
    int,
    float,
    str,
    datetime,
    Value[None],
    Value[bool],
    Value[int],
    Value[float],
    Value[str],
    Value[datetime],
]
UrlParameter = Union[UrlParameterValue, List[UrlParameterValue]]
UrlParameters = Union[str, Mapping[str, UrlParameter]]
ResolvedUrlParameterValue = Optional[str]
ResolvedUrlParameter = Union[
    ResolvedUrlParameterValue,
    List[ResolvedUrlParameterValue],
]
ResolvedUrlParameters = Union[str, Mapping[str, ResolvedUrlParameter]]


def resolve_param_value(value: UrlParameterValue, **kwargs) -> Optional[str]:
    if isinstance(value, Value):
        value = value.apply_context(**kwargs)

    if value is None:
        return None
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def resolve_param(param: UrlParameter, **kwargs) -> ResolvedUrlParameter:
    if isinstance(param, list):
        return [resolve_param_value(value, **kwargs) for value in param]
    return resolve_param_value(param)


def resolve_params(params: UrlParameters, **kwargs) -> ResolvedUrlParameters:
    if isinstance(params, str):
        return params
    return {
        key: resolve_param(param, **kwargs)
        for (key, param) in params.items()
    }
