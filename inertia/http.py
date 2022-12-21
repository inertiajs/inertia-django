from django.http import JsonResponse
from django.shortcuts import render as base_render
from .settings import settings
from json import dumps as json_encode
from functools import wraps
import requests
from .utils import LazyProp

def render(request, component, props={}, template_data={}):
  def is_a_partial_render():
    return 'X-Inertia-Partial-Data' in request.headers and request.headers.get('X-Inertia-Partial-Component', '') == component

  def partial_keys():
    return request.headers.get('X-Inertia-Partial-Data', '').split(',')

  def deep_transform_callables(prop):
    if not isinstance(prop, dict):
      return prop() if callable(prop) else prop
    
    for key in list(prop.keys()):
      prop[key] = deep_transform_callables(prop[key])

    return prop

  def build_props():
    _props = {
      **(request.inertia.all() if hasattr(request, 'inertia') else {}),
      **props,
    }

    for key in list(_props.keys()):
      if is_a_partial_render():
        if key not in partial_keys():
          del _props[key]
      else:
        if isinstance(_props[key], LazyProp):
          del _props[key]

    return deep_transform_callables(_props)

  def render_ssr():
    response = requests.post(f'{settings.INERTIA_SSR_URL}/render', json=page_data())
    response.raise_for_status()
    return base_render(request, 'inertia_ssr.html', {
     'inertia_layout': settings.INERTIA_LAYOUT,
      **response.json()
    })

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
    try:
      return render_ssr()
    except Exception:
      pass
  
  return base_render(request, 'inertia.html', {
    'inertia_layout': settings.INERTIA_LAYOUT,
    'page': json_encode(page_data(), cls=settings.INERTIA_JSON_ENCODER),
    **template_data,
  })

def inertia(component):
  def decorator(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
      props = func(request, *args, **kwargs)

      # if something other than a dict is returned, the user probably wants to return a specific response
      if not isinstance(props, dict):
        return props

      return render(request, component, props)
    
    return inner
  
  return decorator
