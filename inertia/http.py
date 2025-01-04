from http import HTTPStatus
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render as base_render
from .settings import settings
from json import dumps as json_encode
from functools import wraps
import requests
from .utils import DeferredProp, LazyProp

INERTIA_REQUEST_ENCRYPT_HISTORY = "_inertia_encrypt_history"
INERTIA_SESSION_CLEAR_HISTORY = "_inertia_clear_history"

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
        if isinstance(_props[key], LazyProp) or isinstance(_props[key], DeferredProp):
          del _props[key]

    return deep_transform_callables(_props)

  def build_deferred_props():
    if is_a_partial_render():
      return None

    _deferred_props = {}
    for key, prop in props.items():
      if isinstance(prop, DeferredProp):
        _deferred_props.setdefault(prop.group, []).append(key)

    return _deferred_props
          
  def render_ssr():
    data = json_encode(page_data(), cls=settings.INERTIA_JSON_ENCODER)
    response = requests.post(
      f"{settings.INERTIA_SSR_URL}/render",
      data=data,
      headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    return base_render(request, 'inertia_ssr.html', {
     'inertia_layout': settings.INERTIA_LAYOUT,
      **response.json()
    })

  def page_data():
    encrypt_history = getattr(request, INERTIA_REQUEST_ENCRYPT_HISTORY, settings.INERTIA_ENCRYPT_HISTORY)
    if not isinstance(encrypt_history, bool):
      raise TypeError(f"Expected boolean for encrypt_history, got {type(encrypt_history).__name__}")

    clear_history = request.session.pop(INERTIA_SESSION_CLEAR_HISTORY, False)
    if not isinstance(clear_history, bool):
      raise TypeError(f"Expected boolean for clear_history, got {type(clear_history).__name__}")

    _page = {
      'component': component,
      'props': build_props(),
      'url': request.build_absolute_uri(),
      'version': settings.INERTIA_VERSION,
      'encryptHistory': encrypt_history,
      'clearHistory': clear_history,
    }

    _deferred_props = build_deferred_props()
    if _deferred_props:
      _page['deferredProps'] = _deferred_props
    
    return _page

  if 'X-Inertia' in request.headers:
    return JsonResponse(
      data=page_data(),
      headers={
        'Vary': 'X-Inertia',
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

def location(location):
    return HttpResponse('', status=HTTPStatus.CONFLICT, headers={
      'X-Inertia-Location': location,
    })

def encrypt_history(request, value=True):
  setattr(request, INERTIA_REQUEST_ENCRYPT_HISTORY, value)

def clear_history(request):
  request.session[INERTIA_SESSION_CLEAR_HISTORY] = True

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
