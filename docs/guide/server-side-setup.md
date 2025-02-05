# Server-side setup

To get started with Inertia in Django, the first step is to configure Django to use the `inertia-django` server-side adapter.

::: tip
For new projects, we recommend following the [template based setup](#template-based-setup) guide.
:::

## Template-based setup

If you're starting a new project, we recommend configuring Django and Inertia using a `django-vite-inertia` template.

This will require [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/stable/) to be installed.

First, let's create a new directory for our project.

```shell
mkdir myproject
```
Next, we'll use the template based installer.

::: code-group

```shell [uv]
uvx copier copy gh:sarthakjariwala/django-vite-inertia myproject
```

```shell [pipx]
pipx run copier copy gh:sarthakjariwala/django-vite-inertia myproject

```

:::

This command will:

- Create a new Django project in your `myproject` directory
- Ask you to choose your preferred frontend framework:
    - React
    - Vue
    - Svelte
- Ask you if you want to use Tailwind CSS
- Ask you the database you want to use
    - SQLite
    - PostgreSQL
- Ask you if you want to use Docker in development
- Ask you if you want to use Docker in production
- Set up Vite integration via `django-vite`
- Set up Django to work with Inertia
- Initialize the Inertia app
- Configure CSRF to work properly with Django

Example output:
```
? Your project name: todo
? Which database do you want to use? postgresql
? Which frontend do you want to use? vue
? Do you want to use Tailwind CSS? Yes
? Do you want to use Docker in development? Yes
? Do you want to use Docker in production? Yes
```

You're all set! You can now start your development server.

## Manual setup

::: tip
Skip this section if you used the [template based setup](#template-based-setup) method.
:::

### Install dependencies

Install the `inertia-django` server-side adapter and related dependencies.

::: code-group

```shell [uv]
uv add inertia-django django-vite
```

```shell [pip]
python -m pip install inertia-django django-vite
```
:::

### Update installed apps

Add `django_vite` and `inertia` to your `INSTALLED_APPS` in `settings.py`.

```python
INSTALLED_APPS = [
    # ...
    "django_vite",
    "inertia",
]
```

### Update middleware

Next, add `inertia.middleware.InertiaMiddleware` to your `MIDDLEWARE` in `settings.py`.

```python
MIDDLEWARE = [
    # ...
    "inertia.middleware.InertiaMiddleware",
]
```

### Configure settings

Configure `django-vite` and `inertia-django` specific settings in `settings.py`.

```python
# django-vite settings
# If using HMR (hot module replacement)
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_host": env.str("DJANGO_VITE_DEV_SERVER_HOST", default="localhost"),
        "dev_server_port": env.int("DJANGO_VITE_DEV_SERVER_PORT", default=5173),
    }
}

# Where ViteJS assets are built.
DJANGO_VITE_ASSETS_PATH = BASE_DIR / "src" / "dist"

# Include DJANGO_VITE_ASSETS_PATH into STATICFILES_DIRS to be copied inside
# when run command python manage.py collectstatic
STATICFILES_DIRS = [DJANGO_VITE_ASSETS_PATH]
```

> For a complete list of available `vite` related settings, see `django-vite` [docs](https://github.com/MrBin99/django-vite?tab=readme-ov-file#django-vite).

```python
# inertia-django settings
INERTIA_LAYOUT = "base.html" # update with your base template name
```

> For a complete list of available `inertia-django` settings, see [readme](https://github.com/inertiajs/inertia-django?tab=readme-ov-file#settings).

### Update base template

In your base html template, add the following:

```html
{% load django_vite %}

...
<head>
    ...
    {% vite_hmr_client %}
    {% vite_asset 'js/main.js' %}
</head>

<body>
    {% block inertia %}{% endblock %}
</body>
```
