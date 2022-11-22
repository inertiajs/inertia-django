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

#### Vite Installation

Before you start it's recommended to start a new app. For this example we created a app called `core`.

Install the following python packages via pip
```bash
pip install django-vite whitenoise
```

Create a layout template file
```html
{% load django_vite %}
<!DOCTYPE  html>
<html  lang="en">
<head>
	<meta  charset="UTF-8"  />
	<meta  http-equiv="X-UA-Compatible"  content="IE=edge"  />
	<meta  name="viewport"  content="width=device-width, initial-scale=1.0"  />
	{% vite_hmr_client %}
	{% vite_asset 'main.ts' %}
	
	<title>Inertia Layout</title>
</head>

<body>
	{% block inertia %}{% endblock %}
</body>
</html>
```

Add the Inertia app to your `INSTALLED_APPS` in `settings.py`
```
INSTALLED_APPS = [
  # django apps,
  'inertia',
  'django_vite',
  # your project's apps,
]
```

Add whitenoise middleware in `settings.py`
```python
MIDDLEWARE = [
    # ...
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...
]
```

Add the following in `settings.py`
```python
import re

# django-vite settings

# https://github.com/MrBin99/django-vite
DJANGO_VITE_DEV_MODE = DEBUG  # follow Django's dev mode

# Where ViteJS assets are built.
DJANGO_VITE_ASSETS_PATH = BASE_DIR / "core" / "static" / "dist"

# If use HMR or not. We follow Django's DEBUG mode
DJANGO_VITE_DEV_MODE = DEBUG

# Vite 3 defaults to 5173. Default for django-vite is 3000, which is the default for Vite 2.
DJANGO_VITE_DEV_SERVER_PORT = 5173

STATICFILES_DIRS = [DJANGO_VITE_ASSETS_PATH]

# Inertia settings
INERTIA_LAYOUT = BASE_DIR / "core" / "templates/index.html"

# Vite generates files with 8 hash digits
# http://whitenoise.evans.io/en/stable/django.html#WHITENOISE_IMMUTABLE_FILE_TEST
def  immutable_file_test(path, url):
	# Match filename with 12 hex digits before the extension
	# e.g. app.db8f2edc0c8a.js
	return  re.match(r"^.+\.[0-9a-f]{8,12}\..+$", url)

WHITENOISE_IMMUTABLE_FILE_TEST = immutable_file_test
```

This will be all for the frontend side.

### Frontend

Easiest way to start is by creating a new vite app. In this example we create a svelte-ts vite project outside the django directory.

```bash
# npm 6.x  npm create vite@latest my-vue-app --template vue  # npm 7+, extra double-dash is needed:  npm create vite@latest my-vue-app -- --template vue  # yarn  yarn create vite my-vue-app --template vue  # pnpm  pnpm create vite my-vue-app --template svelte-ts
```

Then copy `vite.config.js` `package.json` to the root folder of your django app.

Modify `vite.config.js`
```javascript
import { defineConfig } from  'vite'
import { resolve } from  "path"
import { svelte } from  '@sveltejs/vite-plugin-svelte'
// https://vitejs.dev/config/

export  default  defineConfig({
	plugins: [svelte({ prebundleSvelteLibraries:  true })],
	root:  resolve("./core/static/src"),
	base:  "/static/",
	build: {
		outDir:  resolve("./core/static/dist"),
		assetsDir:  "",
		manifest:  true,
		emptyOutDir:  true,
		rollupOptions: {
			// Overwrite default .html entry to main.ts in the static directory
			input:  resolve("./core/static/src/main.ts"),
		},
	},
})
```

In `core/static/` we create a `dist` and `src` folder
And in `core/static/src/main.ts` we setup inertia.

```typescript
import  'vite/modulepreload-polyfill'
import { createInertiaApp } from  '@inertiajs/inertia-svelte'
import { InertiaProgress } from  '@inertiajs/progress'

const  pages = import.meta.glob('./**/*.svelte')

InertiaProgress.init()

createInertiaApp({
  resolve:  name  =>  pages[`./pages/${name}.svelte`](),
  setup({ el, App, props }) {
	  new  App({ target:  el, props })
  },
})
```

The frontend part works the same for most frameworks. So it's easy to modify.
For the vitejs svelte plugin `prebundleSvelteLibraries:  true` must be set for it to work.

You can also check out the official Inertia docs at https://inertiajs.com/. 

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

### Lazy Props
On the front end, Inertia supports the concept of "partial reloads" where only the props requested
are returned by the server. Sometimes, you may want to use this flow to avoid processing a particularly slow prop on the intial load. In this case, you can use `Lazy props`. Lazy props aren't evaluated unless they're specifically requested by name in a partial reload.

```python
from inertia import lazy, inertia

@inertia('ExampleComponent')
def example(request):
  return {
    'name': lambda: 'Brandon', # this will be rendered on the first load as usual
    'data': lazy(lambda: some_long_calculation()), # this will only be run when specifically requested by partial props and WILL NOT be included on the initial load
  }
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

Inertia Django has a few different settings options that can be set from within your project's `settings.py` file. Some of them have defaults.

The default config is shown below

```python
INERTIA_VERSION = '1.0' # defaults to '1.0'
INERTIA_LAYOUT = 'layout.html' # required and has no default
INERTIA_JSON_ENCODER = CustomJsonEncoder # defaults to inertia.utils.InertiaJsonEncoder
INERTIA_SSR_URL = 'http://localhost:13714' # defaults to http://localhost:13714
INERTIA_SSR_ENABLED = False # defaults to False
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

## Thank you

A huge thank you to the community members who have worked on InertiaJS for Django before us. Parts of this repo were particularly inspired by [Andres Vargas](https://github.com/zodman) and [Samuel Girardin](https://github.com/girardinsamuel). Additional thanks to Andres for the Pypi project.

*Maintained and sponsored by the team at [bellaWatt](https://bellawatt.com/)*

[![bellaWatt Logo](https://user-images.githubusercontent.com/6599653/114456832-5607d980-9bab-11eb-99c8-ab39867c384e.png)](https://bellawatt.com/)
