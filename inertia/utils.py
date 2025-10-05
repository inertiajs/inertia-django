import warnings
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict as base_model_to_dict

from .prop_classes import DeferredProp, MergeProp, OptionalProp


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


def optional(prop: Any) -> OptionalProp:
    return OptionalProp(prop)


def defer(prop: Any, group: str = "default", merge: bool = False) -> DeferredProp:
    return DeferredProp(prop, group=group, merge=merge)


def merge(prop: Any) -> MergeProp:
    return MergeProp(prop)
