from datetime import date, datetime
from json import dumps

from django.test import TestCase

from inertia.tests.testapp.models import Sport, User
from inertia.utils import InertiaJsonEncoder


def make_brandon() -> User:
    return User(
        name="Brandon",
        password="something-top-secret",
        birthdate=date(1987, 2, 15),
        registered_at=datetime(2022, 10, 31, 10, 13, 1),
    )


class InertiaJsonEncoderTestCase(TestCase):
    def setUp(self):
        self.encode = lambda obj: dumps(obj, cls=InertiaJsonEncoder)

    def test_it_handles_models_with_dates_and_removes_passwords(self):
        user = make_brandon()

        self.assertEqual(
            dumps(
                {
                    "id": None,
                    "name": "Brandon",
                    "birthdate": "1987-02-15",
                    "registered_at": "2022-10-31T10:13:01",
                }
            ),
            self.encode(user),
        )

    def test_it_handles_inertia_meta_fields(self):
        sport = Sport(
            id=3,
            name="Hockey",
            season="Winter",
            created_at=datetime(2022, 10, 31, 10, 13, 1),
        )

        self.assertEqual(
            dumps(
                {
                    "id": 3,
                    "name": "Hockey",
                    "created_at": "2022-10-31T10:13:01",
                }
            ),
            self.encode(sport),
        )

    def test_it_handles_querysets(self):
        make_brandon().save()

        self.assertEqual(
            dumps(
                [
                    {
                        "id": 1,
                        "name": "Brandon",
                        "birthdate": "1987-02-15",
                        "registered_at": "2022-10-31T10:13:01",
                    }
                ]
            ),
            self.encode(User.objects.all()),
        )

    def test_it_handles_non_model_querysets(self):
        user = make_brandon()
        user.save()
        self.assertEqual(
            self.encode(User.objects.values_list("name", flat=True)),
            self.encode([user.name]),
        )
