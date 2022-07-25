from django.http import JsonResponse
from django.shortcuts import render as base_render
from .settings import settings
from json import dumps as json_encode
from functools import wraps
import requests

def render(request, component, props={}, view_data={}):
  def build_props():
    _props = {
      **(request.inertia.all() if hasattr(request, 'inertia') else {}),
      **props,
    }

    for key, value in _props.items():
      if callable(value):
        _props[key] = value()

    return _props

  def render_ssr():
    response = requests.post(f'{settings.INERTIA_SSR_URL}/render', json=page_data()).json()
    return base_render(request, 'inertia_ssr.html', response)

  def page_data():
    return {
      'component': component,
      'props': build_props(),
      'url': request.build_absolute_uri(),
      'version': settings.INERTIA_VERSION,
    }

  if 'X-Inertia' in request.headers:
    return JsonResponse(
      data=page_data(),
      headers={
        'Vary': 'Accept',
        'X-Inertia': 'true',
      },
      encoder=settings.INERTIA_JSON_ENCODER,
    )

  if settings.INERTIA_SSR_ENABLED:
    return render_ssr()
  
  return base_render(request, 'inertia.html', {
    'inertia_layout': settings.INERTIA_LAYOUT,
    'page': json_encode(page_data(), cls=settings.INERTIA_JSON_ENCODER),
    **view_data,
  })

def inertia(component):
  def decorator(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
      props = func(request, *args, **kwargs)
      return render(request, component, props)
    
    return inner
  
  return decorator
