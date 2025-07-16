import warnings

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict as base_model_to_dict

from .prop_classes import DeferredProp, MergeProp, OptionalProp


def model_to_dict(model):
    return base_model_to_dict(model, exclude=("password",))


class InertiaJsonEncoder(DjangoJSONEncoder):
    def default(self, o):
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


def lazy(prop):
    warnings.warn(
        "lazy is deprecated and will be removed in a future version. Please use optional instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return optional(prop)


def optional(prop):
    return OptionalProp(prop)


def defer(prop, group="default", merge=False):
    return DeferredProp(prop, group=group, merge=merge)


def merge(prop):
    return MergeProp(prop)
