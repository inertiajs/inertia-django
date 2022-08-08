from django.test import TestCase, Client
from unittest.mock import patch
from django.http.response import JsonResponse
from inertia.settings import settings
from json import dumps, loads
from django.utils.html import escape
from django.shortcuts import render

class BaseInertiaTestCase:
  def setUp(self):
    self.inertia = Client(HTTP_X_INERTIA=True)

  def assertJSONResponse(self, response, json_obj):
    self.assertIsInstance(response, JsonResponse)
    self.assertEqual(response.json(), json_obj)

class InertiaTestCase(BaseInertiaTestCase, TestCase):
  def setUp(self):
    super().setUp()

    self.mock_inertia = patch('inertia.http.base_render', wraps=render)
    self.mock_render = self.mock_inertia.start()

  def tearDown(self):
    self.mock_inertia.stop()

  def page(self):
    return loads(self.mock_render.call_args.args[2]['page'])

  def props(self):
    return self.page()['props']

  def template_data(self):
    context = self.mock_render.call_args.args[2]

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

def inertia_page(url, component='TestComponent', props={}, template_data={}):
  return {
    'component': 'TestComponent',
    'props': props,
    'url': f'http://testserver/{url}/',
    'version': settings.INERTIA_VERSION,
  }

def inertia_div(*args, **kwargs):
  page = inertia_page(*args, **kwargs)
  return f'<div id="app" data-page="{escape(dumps(page))}"></div>'