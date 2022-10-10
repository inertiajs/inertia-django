from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import decorator_from_middleware
from inertia import inertia, render, lazy, share

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