from .settings import settings
from django.contrib import messages
from django.http import HttpResponse
from django.middleware.csrf import get_token

class InertiaMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response
  
  def __call__(self, request):
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

  def is_non_post_redirect(self, request, response):
    return self.is_redirect_request(response) and request.method in ['POST', 'PATCH', 'DELETE']

  def is_inertia_request(self, request):
    return 'X-Inertia' in request.headers

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