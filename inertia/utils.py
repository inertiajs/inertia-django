from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict as base_model_to_dict
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

class LazyProp:
  def __init__(self, prop):
    warnings.warn(
      "lazy and LazyProp are deprecated and will be removed in a future version. Please use optional instead.",
      DeprecationWarning,
      stacklevel=2
    )
    self.prop = prop

  def __call__(self):
    return self.prop() if callable(self.prop) else self.prop

class OptionalProp(LazyProp):
  def __init__(self, prop):
    self.prop = prop
  
class DeferredProp:
  def __init__(self, prop, group):
    self.prop = prop
    self.group = group

  def __call__(self):
    return self.prop() if callable(self.prop) else self.prop

def lazy(prop):
  return LazyProp(prop)

def optional(prop):
  return OptionalProp(prop)

def defer(prop, group="default"):
  return DeferredProp(prop, group)
