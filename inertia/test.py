from json import dumps, loads
from unittest.mock import patch

from django.template.loader import render_to_string as base_render_to_string
from django.test import Client, TestCase

from inertia.settings import settings


class ClientWithLastResponse:
    def __init__(self, client):
        self.client = client
        self.last_response = None

    def get(self, *args, **kwargs):
        self.last_response = self.client.get(*args, **kwargs)
        return self.last_response

    def post(self, *args, **kwargs):
        self.last_response = self.client.post(*args, **kwargs)
        return self.last_response

    def put(self, *args, **kwargs):
        self.last_response = self.client.put(*args, **kwargs)
        return self.last_response

    def patch(self, *args, **kwargs):
        self.last_response = self.client.patch(*args, **kwargs)
        return self.last_response

    def delete(self, *args, **kwargs):
        self.last_response = self.client.delete(*args, **kwargs)
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
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.json(), json_obj)


class InertiaTestCase(BaseInertiaTestCase, TestCase):
    def setUp(self):
        super().setUp()

        self.mock_inertia = patch(
            "inertia.http.render_to_string", wraps=base_render_to_string
        )
        self.mock_render = self.mock_inertia.start()

    def tearDown(self):
        self.mock_inertia.stop()

    def page(self):
        page_data = (
            self.mock_render.call_args[0][1]["page"]
            if self.mock_render.call_args
            else self.last_response().content
        )

        return loads(page_data)

    def props(self):
        return self.page()["props"]

    def merge_props(self):
        return self.page()["mergeProps"]

    def deferred_props(self):
        return self.page()["deferredProps"]

    def once_props(self):
        return self.page()["onceProps"]

    def template_data(self):
        context = self.mock_render.call_args[0][1]
        return {
            key: context[key]
            for key in context
            if key not in ["page", "inertia_layout"]
        }

    def component(self):
        return self.page()["component"]

    def assertIncludesProps(self, props):
        self.assertDictEqual(self.props(), {**self.props(), **props})

    def assertHasExactProps(self, props):
        self.assertDictEqual(self.props(), props)

    def assertIncludesTemplateData(self, template_data):
        self.assertDictEqual(
            self.template_data(), {**self.template_data(), **template_data}
        )

    def assertHasExactTemplateData(self, template_data):
        self.assertDictEqual(self.template_data(), template_data)

    def assertComponentUsed(self, component_name):
        self.assertEqual(component_name, self.component())


def inertia_page(
    url,
    component="TestComponent",
    props=None,
    template_data=None,
    deferred_props=None,
    merge_props=None,
    once_props=None,
    preserve_fragment=False,
    prepend_props=None,
    shared_props=None,
):
    props = props or {}
    template_data = template_data or {}
    _page = {
        "component": component,
        "props": props,
        "url": f"/{url}/",
        "version": settings.INERTIA_VERSION,
        "encryptHistory": False,
        "clearHistory": False,
    }

    if preserve_fragment:
        _page["preserveFragment"] = True

    if deferred_props:
        _page["deferredProps"] = deferred_props

    if merge_props:
        _page["mergeProps"] = merge_props

    if prepend_props:
        _page["prependProps"] = prepend_props

    if once_props:
        _page["onceProps"] = once_props

    if shared_props:
        _page["sharedProps"] = shared_props

    return _page


def inertia_div(*args, **kwargs):
    page = inertia_page(*args, **kwargs)
    data = (
        dumps(page)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )
    return (
        f'<script data-page="app" type="application/json">{data}</script>'
        '\n  <div id="app"></div>'
    )
