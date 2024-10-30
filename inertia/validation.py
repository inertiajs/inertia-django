from typing import Union

from django.forms import Form
from django.forms.utils import ErrorDict
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

VALIDATION_ERRORS_SESSION_KEY = "_inertia_validation_errors"

InertiaRedirect = Union[HttpResponseRedirect, HttpResponsePermanentRedirect]


class InertiaValidationError(Exception):
  def __init__(self, errors: ErrorDict, redirect: InertiaRedirect):
    super().__init__()
    self.redirect = redirect
    self.errors = errors


def inertia_validate(form: Form, redirect: InertiaRedirect):
  if not form.is_valid():
    raise InertiaValidationError(form.errors, redirect)

  return form.cleaned_data
