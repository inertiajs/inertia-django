from django.conf import settings as django_settings
from .utils import InertiaJsonEncoder

__all__ = ['settings']

class InertiaSettings:
  INERTIA_VERSION = '1.0'
  INERTIA_JSON_ENCODER = InertiaJsonEncoder
  INERTIA_SSR_URL = 'http://localhost:13714'
  INERTIA_SSR_ENABLED = False
  
  def __getattribute__(self, name):
    try:
      return getattr(django_settings, name)
    except AttributeError:
      return super().__getattribute__(name)

settings = InertiaSettings()
