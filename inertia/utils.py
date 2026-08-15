import warnings
from datetime import datetime, timedelta
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict as base_model_to_dict

from .prop_classes import (
    AlwaysProp,
    DeferredProp,
    MergeProp,
    OnceProp,
    OptionalProp,
    ScrollProp,
)


def model_to_dict(model: models.Model) -> dict[str, Any]:
    return base_model_to_dict(model, exclude=("password",))


class InertiaJsonEncoder(DjangoJSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o.__class__, "InertiaMeta"):
            return {
                field: getattr(o, field) for field in o.__class__.InertiaMeta.fields
            }
        if isinstance(o, models.Model):
            return model_to_dict(o)
        if isinstance(o, QuerySet):
            return [
                (model_to_dict(obj) if isinstance(o.model, models.Model) else obj)
                for obj in o
            ]
        return super().default(o)


def lazy(prop: Any) -> OptionalProp:
    warnings.warn(
        "lazy is deprecated and will be removed in a future version. Please use optional instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return optional(prop)


def optional(prop: Any, **once_options: Any) -> OptionalProp:
    return OptionalProp(prop, **once_options)


def always(prop: Any) -> AlwaysProp:
    return AlwaysProp(prop)


def once(
    prop: Any,
    fresh: bool = False,
    *,
    key: str | None = None,
    expires_at: datetime | timedelta | int | float | None = None,
) -> OnceProp:
    return OnceProp(prop, key=key, expires_at=expires_at, fresh=fresh)


def defer(
    prop: Any,
    group: str = "default",
    merge: bool = False,
    *,
    deep_merge: bool = False,
    match_on: str | list[str] | None = None,
    once: bool = False,
    key: str | None = None,
    expires_at: datetime | timedelta | int | float | None = None,
    fresh: bool = False,
    rescue: bool = False,
) -> DeferredProp:
    return DeferredProp(
        prop,
        group,
        merge,
        deep_merge=deep_merge,
        match_on=match_on,
        once=once,
        key=key,
        expires_at=expires_at,
        fresh=fresh,
        rescue=rescue,
    )


def merge(prop: Any, **options: Any) -> MergeProp:
    return MergeProp(prop, **options)


def deep_merge(
    prop: Any, *, match_on: str | list[str] | None = None, **options: Any
) -> MergeProp:
    return MergeProp(prop, deep_merge=True, match_on=match_on, **options)


def scroll(
    prop: Any,
    metadata: dict[str, Any],
    *,
    wrapper: str | None = None,
    defer: bool = False,
    group: str = "default",
) -> ScrollProp:
    normalized = {
        "pageName": metadata["pageName"],
        "previousPage": metadata["previousPage"],
        "nextPage": metadata["nextPage"],
        "currentPage": metadata["currentPage"],
    }
    return ScrollProp(prop, normalized, wrapper=wrapper, defer=defer, group=group)
