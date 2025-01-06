from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import decorator_from_middleware
from inertia import inertia, render, lazy, merge, optional, defer, share, location
from inertia.http import INERTIA_SESSION_CLEAR_HISTORY, clear_history, encrypt_history

class ShareMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def process_request(self, request):
    share(request, 
      position=lambda: 'goalie',
      number=29,
    )

def test(request):
  return HttpResponse('Hey good stuff')

@inertia('TestComponent')
def empty_test(request):
  return {}

def redirect_test(request):
  return redirect(empty_test)

@inertia('TestComponent')
def inertia_redirect_test(request):
  return redirect(empty_test)

def external_redirect_test(request):
  return location("http://foobar.com/")

@inertia('TestComponent')
def props_test(request):
  return {
    'name': 'Brandon',
    'sport': 'Hockey',
  }

def template_data_test(request):
  return render(request, 'TestComponent', template_data={
    'name': 'Brian',
    'sport': 'Basketball',
  })

@inertia('TestComponent')
def lazy_test(request):
  return {
    'name': 'Brian',
    'sport': lazy(lambda: 'Basketball'),
    'grit': lazy(lambda: 'intense'),
  }

@inertia('TestComponent')
def optional_test(request):
  return {
    'name': 'Brian',
    'sport': optional(lambda: 'Basketball'),
    'grit': optional(lambda: 'intense'),
  }

@inertia('TestComponent')
def defer_test(request):
  return {
    'name': 'Brian',
    'sport': defer(lambda: 'Basketball')
  }


@inertia('TestComponent')
def defer_group_test(request):
  return {
    'name': 'Brian',
    'sport': defer(lambda: 'Basketball', 'group'),
    'team': defer(lambda: 'Bulls', 'group'),
    'grit': defer(lambda: 'intense')
  }

@inertia('TestComponent')
def merge_test(request):
  return {
    'name': 'Brandon',
    'sport': merge(lambda: 'Hockey'),
    'team': defer(lambda: 'Penguins', merge=True),
  }

@inertia('TestComponent')
def complex_props_test(request):
  return {
    'person': {
      'name': lambda: 'Brandon',
    }
  }

@decorator_from_middleware(ShareMiddleware)
@inertia('TestComponent')
def share_test(request):
  return {
    'name': 'Brandon',
  }

@inertia('TestComponent')
def encrypt_history_test(request):
  encrypt_history(request)
  return {}

@inertia('TestComponent')
def encrypt_history_false_test(request):
  encrypt_history(request, False)
  return {}

@inertia('TestComponent')
def encrypt_history_type_error_test(request):
  encrypt_history(request, "foo")
  return {}

@inertia('TestComponent')
def clear_history_test(request):
  clear_history(request)
  return {}

@inertia('TestComponent')
def clear_history_redirect_test(request):
  clear_history(request)
  return redirect(empty_test)

@inertia('TestComponent')
def clear_history_type_error_test(request):
  request.session[INERTIA_SESSION_CLEAR_HISTORY] = "foo"
  return {}
