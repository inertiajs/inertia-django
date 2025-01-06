from inertia.http import encrypt_history
from inertia.test import InertiaTestCase
from django.test import override_settings
from django.test.client import RequestFactory
from inertia.tests.testapp.views import empty_test

class HistoryTestCase(InertiaTestCase):
  def test_encrypt_history_setting(self):
    self.client.get('/empty/')
    assert self.page()['encryptHistory'] is False

    with override_settings(INERTIA_ENCRYPT_HISTORY=True):
      self.client.get('/empty/')
      assert self.page()['encryptHistory'] is True

  def test_encrypt_history(self):
    self.client.get('/encrypt-history/')
    assert self.page()['encryptHistory'] is True

    with override_settings(INERTIA_ENCRYPT_HISTORY=True):
      self.client.get('/no-encrypt-history/')
      assert self.page()['encryptHistory'] is False

  def test_clear_history(self):
    self.client.get('/clear-history/')
    assert self.page()['clearHistory'] is True

  def test_clear_history_redirect(self):
    response = self.client.get('/clear-history-redirect/', follow=True)
    self.assertRedirects(response, '/empty/')
    assert self.page()['clearHistory'] is True

  def test_raises_type_error(self):
    with self.assertRaisesMessage(TypeError, 'Expected bool for encrypt_history, got str'):
      self.client.get('/encrypt-history-type-error/')

    with self.assertRaisesMessage(TypeError, 'Expected bool for clear_history, got str'):
      self.client.get('/clear-history-type-error/')
