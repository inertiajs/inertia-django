from django.test import TestCase, Client, override_settings
from inertia.test import InertiaTestCase
from inertia.validation import VALIDATION_ERRORS_SESSION_KEY
from django.conf import settings

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

  def test_stores_validation_errors_in_session(self):
    self.inertia.post('/form/', data={'invalid': 'data'})
    self.assertDictEqual(self.inertia.session[VALIDATION_ERRORS_SESSION_KEY], {
      'str_field': 'This field is required.',
      'num_field': 'This field is required.'
    })

  def test_pops_validation_errors_from_session(self):
    self.inertia.post('/form/', data={'invalid': 'data'})
    self.inertia.get('/form/')
    self.assertFalse(self.inertia.session.has_key(VALIDATION_ERRORS_SESSION_KEY))

  def test_maintains_validation_errors_in_session_until_necessary(self):
    self.inertia.post('/form/', data={'invalid': 'data'})
    # Some other non-inertia request before Inertia actually redirects
    self.client.cookies[settings.SESSION_COOKIE_NAME] = self.inertia.session.session_key
    self.client.get('/empty/')

    self.assertTrue(self.inertia.session.has_key(VALIDATION_ERRORS_SESSION_KEY))
