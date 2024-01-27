from .settings import settings
from django.contrib import messages
from django.http import HttpResponse
from django.middleware.csrf import get_token
from .validation import InertiaValidationError, VALIDATION_ERRORS_SESSION_KEY
from .share import share

class InertiaMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    validation_errors =  request.session.get(VALIDATION_ERRORS_SESSION_KEY, None)

    if self.is_inertia_get_request(request) and validation_errors is not None:
      request.session.pop(VALIDATION_ERRORS_SESSION_KEY)
      request.session.modified = True
      # Must be shared before rendering the response
      share(request, errors=validation_errors)

    response = self.get_response(request)

    # Inertia requests don't ever render templates, so they skip the typical Django
    # CSRF path. We'll manually add a CSRF token for every request here.
    get_token(request)

    if not self.is_inertia_request(request):
      return response

    if self.is_non_post_redirect(request, response):
      response.status_code = 303

    if self.is_stale(request):
      return self.force_refresh(request)

    return response

  def process_exception(self, request, exception):
    if isinstance(exception, InertiaValidationError):
      errors = {field: errors[0] for field, errors in exception.errors.items()}
      request.session[VALIDATION_ERRORS_SESSION_KEY] = errors
      request.session.modified = True
      return exception.redirect

  def is_non_post_redirect(self, request, response):
    return self.is_redirect_request(response) and request.method in ['PUT', 'PATCH', 'DELETE']

  def is_inertia_request(self, request):
    return 'X-Inertia' in request.headers

  def is_inertia_get_request(self, request):
    return request.method == "GET" and self.is_inertia_request(request)

  def is_redirect_request(self, response):
    return response.status_code in [301, 302]

  def is_stale(self, request):
    return request.headers.get('X-Inertia-Version', settings.INERTIA_VERSION) != settings.INERTIA_VERSION

  def is_stale_inertia_get(self, request):
    return request.method == 'GET' and self.is_stale(request)

  def force_refresh(self, request):
    messages.get_messages(request).used = False
    return HttpResponse('', status=409, headers={
      'X-Inertia-Location': request.build_absolute_uri(),
    })