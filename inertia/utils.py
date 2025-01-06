from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict as base_model_to_dict
from .prop_classes import OptionalProp, DeferredProp, MergeProp
import warnings

def model_to_dict(model):
  return base_model_to_dict(model, exclude=('password',))

class InertiaJsonEncoder(DjangoJSONEncoder):
  def default(self, value):
    if isinstance(value, models.Model):
      return model_to_dict(value)
    
    if isinstance(value, QuerySet):
      return [model_to_dict(model) for model in value]
    
    return super().default(value)

def lazy(prop):
  warnings.warn(
    "lazy is deprecated and will be removed in a future version. Please use optional instead.",
    DeprecationWarning,
    stacklevel=2
  )
  return optional(prop)

def optional(prop):
  return OptionalProp(prop)

def defer(prop, group="default", merge=False):
  return DeferredProp(prop, group=group, merge=merge)

def merge(prop):
  return MergeProp(prop)
