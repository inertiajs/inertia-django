import warnings

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict as base_model_to_dict

from .prop_classes import DeferredProp, MergeProp, OptionalProp


def model_to_dict(model):
    return base_model_to_dict(model, exclude=("password",))


class InertiaJsonEncoder(DjangoJSONEncoder):
    def default(self, value):
        if hasattr(value.__class__, "InertiaMeta"):
            return {
                field: getattr(value, field)
                for field in value.__class__.InertiaMeta.fields
            }

        if isinstance(value, models.Model):
            return model_to_dict(value)

        if isinstance(value, QuerySet):
            return [
                (model_to_dict(obj) if isinstance(value.model, models.Model) else obj)
                for obj in value
            ]

        return super().default(value)


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
