from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict as base_model_to_dict

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
    self.prop = prop

  def __call__(self):
    return self.prop() if callable(self.prop) else self.prop
  

def lazy(prop):
  return LazyProp(prop)
