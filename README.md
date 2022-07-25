![image](https://user-images.githubusercontent.com/6599653/114456558-032e2200-9bab-11eb-88bc-a19897f417ba.png)


# Inertia.js Django Adapter

## :warning: Inertia Django is still pre stable release and is not considered production ready like its siblings Inertia Laravel and Inertia Rails. Use at your own risk and please report any issues! :warning:

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

Finally, create a layout which exposes `{% block content %}{% endblock %}` in the body and set the path to this layout as `INERTIA_LAYOUT` in your `settings.py` file.

Now you're all set!

### Frontend

Django specific frontend docs coming soon. For now, we recommend installing [django_vite](https://github.com/MrBin99/django-vite) 
and following the commits on the Django Vite [example repo](https://github.com/MrBin99/django-vite-example). Once Vite is setup with
your frontend of choice, just replace the contents of `entry.js` with [this file (example in react)](https://github.com/BrandonShar/inertia-rails-template/blob/main/app/frontend/entrypoints/application.jsx)


You can also check out the official Inertia docs at https://inertiajs.com/. 

## Usage

### Responses

Render Inertia responses is simple, you can either use the provided inertia render function or, for the most common use case, the inertia decorator. The render function accepts four arguments, the first is your request object. The second is the name of the component you want to render from within your pages directory (without extension). The third argument is a dict of `props` that should be provided to your components. The final argument is `view_data`, for any variables you want to provide to your template, but this is much less common.

```python
from inertia.http import render
from .models import Event

def index(request):
  return render(request, 'Event/Index', props={
    'events': Event.objects.all()
  })
```

Or use the simpler decorator for the most common use cases

```python
from inertia.http import inertia
from .models import Event

@inertia('Event/Index')
def index(request):
  return {
    'events': Event.objects.all(),
  }
```

### Shared Data

If you have data that you want to be provided as a prop to every component (a common use-case is information about the authenticated user) you can use the `share` method. A common place to put this would be in some custom middleware.

```python
from inertia.share import share
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
```

### Json Encoding

Inertia Django ships with a custom JsonEncoder at `inertia.utils.InertiaJsonEncoder` that extends Django's 
`DjangoJSONEncoder` with additional logic to handle encoding models and Querysets. If you have other json 
encoding logic you'd prefer, you can set a new JsonEncoder via the settings.

### SSR 

#### Backend
Enable SSR via the `INERTIA_SSR_URL` and `INERTIA_SSR_ENABLED` settings

#### Frontend
Coming Soon!

## Settings

Inertia Rails has a few different settings options that can be set from within your project's `settings.py` file. Some of them have defaults.

The default config is shown below

```python
INERTIA_VERSION = '1.0' # defaults to '1.0'
INERTIA_LAYOUT = 'layout.html' # required and has no default
INERTIA_JSON_ENCODER = CustomJsonEncoder # defaults to inertia.utils.InertiaJsonEncoder
INERTIA_SSR_URL = 'http://localhost:13714' # defaults to http://localhost:13714
INERTIA_SSR_ENABLED = False # defaults to False
```

## Thank you

A huge thank you to the community members who have worked on InertiaJS for Django before us. Parts of this repo were particularly inspired by [Andres Vargas](https://github.com/zodman) and [Samuel Girardin](https://github.com/girardinsamuel). Additional thanks to Andres for the Pypi project.

*Maintained and sponsored by the team at [bellaWatt](https://bellawatt.com/)*

[![bellaWatt Logo](https://user-images.githubusercontent.com/6599653/114456832-5607d980-9bab-11eb-99c8-ab39867c384e.png)](https://bellawatt.com/)
