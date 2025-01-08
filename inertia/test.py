from django.test import TestCase, Client
from unittest.mock import patch
from django.template.loader import render_to_string as base_render_to_string
from inertia.settings import settings
from json import dumps, loads
from django.utils.html import escape

class ClientWithLastResponse:
  def __init__(self, client):
    self.client = client
    self.last_response = None
  
  def get(self, *args, **kwargs):
    self.last_response = self.client.get(*args, **kwargs)
    return self.last_response
  
  def __getattr__(self, name):
    return getattr(self.client, name)

class BaseInertiaTestCase:
  def setUp(self):
    self.inertia = ClientWithLastResponse(Client(HTTP_X_INERTIA=True))
    self.client = ClientWithLastResponse(Client())
  
  def last_response(self):
    return self.inertia.last_response or self.client.last_response

  def assertJSONResponse(self, response, json_obj):
    self.assertEqual(response.headers['Content-Type'], 'application/json')
    self.assertEqual(response.json(), json_obj)

class InertiaTestCase(BaseInertiaTestCase, TestCase):
  def setUp(self):
    super().setUp()

    self.mock_inertia = patch('inertia.http.render_to_string', wraps=base_render_to_string)
    self.mock_render = self.mock_inertia.start()

  def tearDown(self):
    self.mock_inertia.stop()

  def page(self):
    page_data = self.mock_render.call_args[0][1]['page'] if self.mock_render.call_args else self.last_response().content
    
    return loads(page_data)

  def props(self):
    return self.page()['props']
  
  def merge_props(self):
    return self.page()['mergeProps']
  
  def deferred_props(self):
    return self.page()['deferredProps']

  def template_data(self):
    context = self.mock_render.call_args[0][1]
    return {key: context[key] for key in context if key not in ['page', 'inertia_layout']}

  def component(self):
    return self.page()['component']

  def assertIncludesProps(self, props):
    self.assertDictEqual(self.props(), {**self.props(), **props})

  def assertHasExactProps(self, props):
    self.assertDictEqual(self.props(), props)

  def assertIncludesTemplateData(self, template_data):
    self.assertDictEqual(self.template_data(), {**self.template_data(), **template_data})

  def assertHasExactTemplateData(self, template_data):
    self.assertDictEqual(self.template_data(), template_data)

  def assertComponentUsed(self, component_name):
    self.assertEqual(component_name, self.component())

def inertia_page(url, component='TestComponent', props={}, template_data={}, deferred_props=None, merge_props=None):
  _page = {
    'component': component,
    'props': props,
    'url': f'/{url}/',
    'version': settings.INERTIA_VERSION,
    'encryptHistory': False,
    'clearHistory': False,
  }

  if deferred_props:
    _page['deferredProps'] = deferred_props
  
  if merge_props:
    _page['mergeProps'] = merge_props
    
  return _page

def inertia_div(*args, **kwargs):
  page = inertia_page(*args, **kwargs)
  return f'<div id="app" data-page="{escape(dumps(page))}"></div>'
