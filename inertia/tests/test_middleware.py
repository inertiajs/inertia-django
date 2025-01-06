from django.test import TestCase, Client, override_settings
from inertia.test import InertiaTestCase

class MiddlewareTestCase(InertiaTestCase):
  def test_anything(self):
    response = self.client.get('/test/')

    self.assertEqual(response.status_code, 200)

  def test_stale_versions_are_refreshed(self):
    response = self.inertia.get('/empty/',
      HTTP_X_INERTIA_VERSION='some-nonsense',
    )

    self.assertEqual(response.status_code, 409)
    self.assertEqual(response.headers['X-Inertia-Location'], 'http://testserver/empty/')

  def test_redirect_status(self):
    response = self.inertia.post('/redirect/')
    self.assertEqual(response.status_code, 302)

    for http_method in ['put', 'patch', 'delete']:
      response = getattr(self.inertia, http_method)('/redirect/')

      self.assertEqual(response.status_code, 303)

  def test_a_request_not_from_inertia_is_ignored(self):
    response = self.client.get('/empty/',
      HTTP_X_INERTIA_VERSION='some-nonsense',
    )

    self.assertEqual(response.status_code, 200)

  def test_external_redirect_status(self):
    response = self.inertia.post('/external-redirect/')
    self.assertEqual(response.status_code, 409)
    self.assertIn("X-Inertia-Location", response.headers)
    self.assertEqual(
      "http://foobar.com/", response.headers["X-Inertia-Location"]
    )
