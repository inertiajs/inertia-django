from inertia.tests.testapp.models import User
from django.test import TestCase
from inertia.utils import InertiaJsonEncoder
from json import dumps
from datetime import date, datetime

class InertiaJsonEncoderTestCase(TestCase):
  def setUp(self):
    self.encode = lambda obj: dumps(obj, cls=InertiaJsonEncoder)

  def test_it_handles_models_with_dates_and_removes_passwords(self):
    user = User(
      name='Brandon',
      password='something-top-secret',
      birthdate=date(1987, 2, 15),
      registered_at=datetime(2022, 10, 31, 10, 13, 1),
    )

    self.assertEqual(
      dumps({'id': None, 'name': 'Brandon', 'birthdate': '1987-02-15', 'registered_at': '2022-10-31T10:13:01'}),
      self.encode(user)
    )

  def test_it_handles_querysets(self):
    User(
      name='Brandon',
      password='something-top-secret',
      birthdate=date(1987, 2, 15),
      registered_at=datetime(2022, 10, 31, 10, 13, 1),
    ).save()

    self.assertEqual(
      dumps([{'id': 1, 'name': 'Brandon', 'birthdate': '1987-02-15', 'registered_at': '2022-10-31T10:13:01'}]),
      self.encode(User.objects.all())
    )