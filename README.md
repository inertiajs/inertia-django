![image](https://user-images.githubusercontent.com/6599653/114456558-032e2200-9bab-11eb-88bc-a19897f417ba.png)

# Inertia.js Django Adapter

## Installation

### Backend

Install the following python package via pip

```bash
pip install inertia-django
```

Add the Inertia app to your `INSTALLED_APPS` in `settings.py`

```python
INSTALLED_APPS = [
  # django apps,
  'inertia',
  # your project's apps,
]
```

Add the Inertia middleware to your `MIDDLEWARE` in `settings.py`

```python
MIDDLEWARE = [
  # django middleware,
  'inertia.middleware.InertiaMiddleware',
  # your project's middleware,
]
```

Finally, create a layout which exposes `{% block inertia %}{% endblock %}` in the body and set the path to this layout as `INERTIA_LAYOUT` in your `settings.py` file.

Now you're all set!

### Frontend

Django specific frontend docs coming soon. For now, we recommend installing [django_vite](https://github.com/MrBin99/django-vite)
and following the commits on the Django Vite [example repo](https://github.com/MrBin99/django-vite-example). Once Vite is setup with
your frontend of choice, just replace the contents of `entry.js` with [this file (example in react)](https://github.com/BrandonShar/inertia-rails-template/blob/main/app/frontend/entrypoints/application.jsx)

You can also check out the official Inertia docs at https://inertiajs.com/.

### CSRF

Django's CSRF tokens are tightly coupled with rendering templates so Inertia Django automatically handles adding the CSRF cookie for you to each Inertia response. Because the default names Django users for the CSRF headers don't match Axios (the Javascript request library Inertia uses), we'll need to either modify Axios's defaults OR Django's settings.

**You only need to choose one of the following options, just pick whichever makes the most sense to you!**

In your `entry.js` file

```javascript
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";
```

OR

In your Django `settings.py` file

```python
CSRF_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'
CSRF_COOKIE_NAME = 'XSRF-TOKEN'
```

## Usage

### Responses

Render Inertia responses is simple, you can either use the provided inertia render function or, for the most common use case, the inertia decorator. The render function accepts four arguments, the first is your request object. The second is the name of the component you want to render from within your pages directory (without extension). The third argument is a dict of `props` that should be provided to your components. The final argument is `template_data`, for any variables you want to provide to your template, but this is much less common.

```python
from inertia import render
from .models import Event

def index(request):
  return render(request, 'Event/Index', props={
    'events': Event.objects.all()
  })
```

Or use the simpler decorator for the most common use cases

```python
from inertia import inertia
from .models import Event

@inertia('Event/Index')
def index(request):
  return {
    'events': Event.objects.all(),
  }
```

If you need more control, you can also directly return the InertiaResponse class. It has the same arguments as the render method and subclasses HttpResponse to accept of all its arguments as well.

```python
from inertia import InertiaResponse
from .models import Event

def index(request):
  return InertiaResponse(
    request,
    'Event/Index',
    props={
      'events': Event.objects.all()
    }
  )
```

### Shared Data

If you have data that you want to be provided as a prop to every component (a common use-case is information about the authenticated user) you can use the `share` method. A common place to put this would be in some custom middleware.

```python
from inertia import share
from django.conf import settings
from .models import User

def inertia_share(get_response):
  def middleware(request):
    share(request,
      app_name=settings.APP_NAME,
      user_count=lambda: User.objects.count(), # evaluated lazily at render time
      user=lambda: request.user, # evaluated lazily at render time
    )

    return get_response(request)
  return middleware
```

### External Redirects

It is possible to redirect to an external website, or even another non-Inertia endpoint in your app while handling an Inertia request.
This can be accomplished using a server-side initiated `window.location` visit via the `location` method:

```python
from inertia import location

def external():
    return location("http://foobar.com/")
```

It will generate a `409 Conflict` response and include the destination URL in the `X-Inertia-Location` header.
When this response is received client-side, Inertia will automatically perform a `window.location = url` visit.

### Optional Props

On the front end, Inertia supports the concept of "partial reloads" where only the props requested
are returned by the server. Sometimes, you may want to use this flow to avoid processing a particularly slow prop on the intial load. In this case, you can use `Optional props`. Optional props aren't evaluated unless they're specifically requested by name in a partial reload.

```python
from inertia import optional, inertia

@inertia('ExampleComponent')
def example(request):
  return {
    'name': lambda: 'Brandon', # this will be rendered on the first load as usual
    'data': optional(lambda: some_long_calculation()), # this will only be run when specifically requested by partial props and WILL NOT be included on the initial load
  }
```

### Deferred Props

As of version 2.0, Inertia supports the ability to defer the fetching of props until after the page has been initially rendered. Essentially this is similar to the concept of `Optional props` however Inertia provides convenient frontend components to automatically fetch the deferred props after the page has initially loaded, instead of requiring the user to initiate a reload. For more info, see [Deferred props](https://inertiajs.com/deferred-props) in the Inertia documentation.

To mark props as deferred on the server side use the `defer` function.

```python
from inertia import defer, inertia

@inertia('ExampleComponent')
def example(request):
  return {
    'name': lambda: 'Brandon', # this will be rendered on the first load as usual
    'data': defer(lambda: some_long_calculation()), # this will only be run after the frontend has initially loaded and inertia requests this prop
  }
```

#### Grouping requests

By default, all deferred props get fetched in one request after the initial page is rendered, but you can choose to fetch data in parallel by grouping props together.

```python
from inertia import defer, inertia

@inertia('ExampleComponent')
def example(request):
  return {
    'name': lambda: 'Brandon', # this will be rendered on the first load as usual
    'data': defer(lambda: some_long_calculation()),
    'data1': defer(lambda: some_long_calculation1(), group='group'),
    'data2': defer(lambda: some_long_calculation1(), 'group'),
  }
```

In the example above, the `data1`, and `data2` props will be fetched in one request, while the `data` prop will be fetched in a separate request in parallel. Group names are arbitrary strings and can be anything you choose.

### Merge Props

By default, Inertia overwrites props with the same name when reloading a page. However, there are instances, such as pagination or infinite scrolling, where that is not the desired behavior. In these cases, you can merge props instead of overwriting them.

```python
from inertia import merge, inertia

@inertia('ExampleComponent')
def example(request):
  return {
    'name': lambda: 'Brandon', 
    'data': merge(Paginator(objects, 3)), 
  }
```

You can also combine deferred props with mergeable props to defer the loading of the prop and ultimately mark it as mergeable once it's loaded.

```python
from inertia import defer, inertia

@inertia('ExampleComponent')
def example(request):
  return {
    'name': lambda: 'Brandon', 
    'data': defer(lambda: Paginator(objects, 3), merge=True), 
  }
```

### Json Encoding

Inertia Django ships with a custom JsonEncoder at `inertia.utils.InertiaJsonEncoder` that extends Django's
`DjangoJSONEncoder` with additional logic to handle encoding models and Querysets. If you have other json
encoding logic you'd prefer, you can set a new JsonEncoder via the settings.

### History Encryption

Inertia.js supports [history encryption](https://inertiajs.com/history-encryption) to protect sensitive data in the browser's history state. This is useful when your pages contain sensitive information that shouldn't be stored in plain text in the browser's history. This feature requires HTTPS since it relies on `window.crypto.subtle` which is only available in secure contexts.

You can enable history encryption globally via the `INERTIA_ENCRYPT_HISTORY` setting in your `settings.py`:

```python
INERTIA_ENCRYPT_HISTORY = True
```

For more granular control, you can enable encryption on specific views:

```python
from inertia import encrypt_history, inertia

@inertia('TestComponent')
def encrypt_history_test(request):
    encrypt_history(request)
    return {}

# If you have INERTIA_ENCRYPT_HISTORY = True but want to disable encryption for specific views:
@inertia('PublicComponent')
def public_view(request):
    encrypt_history(request, False)  # Explicitly disable encryption for this view
    return {}
```

When users log out, you might want to clear the history to ensure no sensitive data can be accessed. You can do this by extending the logout view:

```python
from inertia import clear_history
from django.contrib.auth import views as auth_views

class LogoutView(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        clear_history(request)
        return response
```

### SSR 

#### Backend

Enable SSR via the `INERTIA_SSR_URL` and `INERTIA_SSR_ENABLED` settings

#### Frontend

Coming Soon!

## Settings

Inertia Django has a few different settings options that can be set from within your project's `settings.py` file. Some of them have defaults.

The default config is shown below

```python
INERTIA_VERSION = '1.0' # defaults to '1.0'
INERTIA_LAYOUT = 'layout.html' # required and has no default
INERTIA_JSON_ENCODER = CustomJsonEncoder # defaults to inertia.utils.InertiaJsonEncoder
INERTIA_SSR_URL = 'http://localhost:13714' # defaults to http://localhost:13714
INERTIA_SSR_ENABLED = False # defaults to False
INERTIA_ENCRYPT_HISTORY = False # defaults to False
```

## Testing

Inertia Django ships with a custom TestCase to give you some nice helper methods and assertions.
To use it, just make sure your TestCase inherits from `InertiaTestCase`. `InertiaTestCase` inherits from Django's `django.test.TestCase` so it includes transaction support and a client.

```python
from inertia.test import InertiaTestCase

class ExampleTestCase(InertiaTestCase):
  def test_show_assertions(self):
    self.client.get('/events/')

    # check the component
    self.assertComponentUsed('Event/Index')

    # access the component name
    self.assertEqual(self.component(), 'Event/Index')

    # props (including shared props)
    self.assertHasExactProps({name: 'Brandon', sport: 'hockey'})
    self.assertIncludesProps({sport: 'hockey'})

    # access props
    self.assertEquals(self.props()['name'], 'Brandon')

    # template data
    self.assertHasExactTemplateData({name: 'Brian', sport: 'basketball'})
    self.assertIncludesTemplateData({sport: 'basketball'})

    # access template data
    self.assertEquals(self.template_data()['name'], 'Brian')
```

The inertia test helper also includes a special `inertia` client that pre-sets the inertia headers
for you to simulate an inertia response. You can access and use it just like the normal client with commands like `self.inertia.get('/events/')`. When using the inertia client, inertia custom assertions **are not** enabled though, so only use it if you want to directly assert against the json response.

## Examples

- [Django Svelte Template](https://github.com/pmdevita/Django-Svelte-Template) - A Django template and example project demonstrating Inertia with Svelte and SSR.

## Thank you

A huge thank you to the community members who have worked on InertiaJS for Django before us. Parts of this repo were particularly inspired by [Andres Vargas](https://github.com/zodman) and [Samuel Girardin](https://github.com/girardinsamuel). Additional thanks to Andres for the Pypi project.

_Maintained and sponsored by the team at [bellaWatt](https://bellawatt.com/)_

[![bellaWatt Logo](https://user-images.githubusercontent.com/6599653/114456832-5607d980-9bab-11eb-99c8-ab39867c384e.png)](https://bellawatt.com/)
