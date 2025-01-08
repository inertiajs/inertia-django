from http import HTTPStatus
from django.template.loader import render_to_string
from django.http import HttpResponse
from .settings import settings
from json import dumps as json_encode
from functools import wraps
import requests
from .prop_classes import IgnoreOnFirstLoadProp, DeferredProp, MergeableProp
from .helpers import deep_transform_callables, validate_type

INERTIA_REQUEST_ENCRYPT_HISTORY = "_inertia_encrypt_history"
INERTIA_SESSION_CLEAR_HISTORY = "_inertia_clear_history"

INERTIA_TEMPLATE = 'inertia.html'
INERTIA_SSR_TEMPLATE = 'inertia_ssr.html'

class InertiaRequest:
  def __init__(self, request):
    self.request = request
  
  def __getattr__(self, name):
    return getattr(self.request, name)
  
  @property
  def headers(self):
    return self.request.headers
  
  @property
  def inertia(self):
    return self.request.inertia.all() if hasattr(self.request, 'inertia') else {}
  
  def is_a_partial_render(self, component):
    return 'X-Inertia-Partial-Data' in self.headers and self.headers.get('X-Inertia-Partial-Component', '') == component

  def partial_keys(self):
    return self.headers.get('X-Inertia-Partial-Data', '').split(',')
  
  def reset_keys(self):
    return self.headers.get('X-Inertia-Reset', '').split(',')
  
  def is_inertia(self):
    return 'X-Inertia' in self.headers

  def should_encrypt_history(self):
    return validate_type(
      getattr(self.request, INERTIA_REQUEST_ENCRYPT_HISTORY, settings.INERTIA_ENCRYPT_HISTORY),
      expected_type=bool,
      name="encrypt_history"
    )

class BaseInertiaResponseMixin:
  def page_data(self):
    clear_history = validate_type(
      self.request.session.pop(INERTIA_SESSION_CLEAR_HISTORY, False),
      expected_type=bool,
      name="clear_history"
    )
      
    _page = {
      'component': self.component,
      'props': self.build_props(),
      'url': self.request.get_full_path(),
      'version': settings.INERTIA_VERSION,
      'encryptHistory': self.request.should_encrypt_history(),
      'clearHistory': clear_history,
    }

    _deferred_props = self.build_deferred_props()
    if _deferred_props:
      _page['deferredProps'] = _deferred_props
    
    _merge_props = self.build_merge_props()
    if _merge_props:
      _page['mergeProps'] = _merge_props
    
    return _page

  def build_props(self):
    _props = {
      **(self.request.inertia),
      **self.props,
    }

    for key in list(_props.keys()):
      if self.request.is_a_partial_render(self.component):
        if key not in self.request.partial_keys():
          del _props[key]
      else:
        if isinstance(_props[key], IgnoreOnFirstLoadProp):
          del _props[key]

    return deep_transform_callables(_props)

  def build_deferred_props(self):
    if self.request.is_a_partial_render(self.component):
      return None

    _deferred_props = {}
    for key, prop in self.props.items():
      if isinstance(prop, DeferredProp):
        _deferred_props.setdefault(prop.group, []).append(key)

    return _deferred_props

  def build_merge_props(self):
    return [
      key 
      for key, prop in self.props.items()
      if (
        isinstance(prop, MergeableProp)
        and prop.should_merge()
        and key not in self.request.reset_keys()
      )
    ]
  
  def build_first_load(self, data):
    context, template = self.build_first_load_context_and_template(data)

    return render_to_string(
      template,
      {
        'inertia_layout': settings.INERTIA_LAYOUT,
        **context,
      },
      self.request,
      using=None,
    )

  
  def build_first_load_context_and_template(self, data):
    if settings.INERTIA_SSR_ENABLED:
      try: 
        response = requests.post(
          f"{settings.INERTIA_SSR_URL}/render",
          data=data,
          headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return {
          **response.json(),
          **self.template_data,
        }, INERTIA_SSR_TEMPLATE
      except Exception:
        pass
    
    return {
      'page': data,
      **(self.template_data),
    }, INERTIA_TEMPLATE


class InertiaResponse(BaseInertiaResponseMixin, HttpResponse):
  json_encoder = settings.INERTIA_JSON_ENCODER

  def __init__(self, request, component, props=None, template_data=None, headers=None, *args, **kwargs):
    self.request = InertiaRequest(request)
    self.component = component
    self.props = props or {}
    self.template_data = template_data or {}
    _headers = headers or {}

    data = json_encode(self.page_data(), cls=self.json_encoder)

    if self.request.is_inertia():
      _headers = {
        **_headers,
        'Vary': 'X-Inertia',
        'X-Inertia': 'true',
        'Content-Type': 'application/json',
      }
      content = data
    else:    
      content = self.build_first_load(data)
    
    super().__init__(
      content=content,
      headers=_headers,
      *args,
      **kwargs,
    )

def render(request, component, props=None, template_data=None):
  return InertiaResponse(
    request,
    component,
    props or {},
    template_data or {}
  )

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
