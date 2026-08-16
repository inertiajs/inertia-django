# Upgrading to Inertia v3

Inertia v3 adds a new client protocol for partial reloads, once props, prop merging, scroll data, and flash messages. Upgrade your client-side packages and then work through the changes below.

## Upgrade the client adapter

Install the v3 adapter for your frontend framework:

::: code-group

```shell [Vue]
npm install @inertiajs/vue3@^3
```

```shell [React]
npm install @inertiajs/react@^3
```

```shell [Svelte]
npm install @inertiajs/svelte@^3
```

:::

## Update custom first-load templates

The built-in `inertia.html` template already uses the v3 format. If your project overrides that template, replace the legacy `data-page` attribute on the app element with a JSON script followed by the app element:

```django
{% extends inertia_layout %}

{% block inertia %}
  <script data-page="app" type="application/json">{{ page|safe }}</script>
  <div id="app"></div>
{% endblock inertia %}
```

The adapter escapes page data before rendering it in this script. Keep the default `id="app"`, or pass a matching `id` option to `createInertiaApp`.

## Configure Django CSRF names

The v3 HTTP client defaults to Laravel's `XSRF-TOKEN` cookie and `X-XSRF-TOKEN` header. Django defaults to `csrftoken` and `X-CSRFToken`, so configure the Inertia client with Django's names:

```js
createInertiaApp({
  // resolve and setup...
  http: {
    xsrfCookieName: "csrftoken",
    xsrfHeaderName: "X-CSRFToken",
  },
})
```

If you customize `CSRF_COOKIE_NAME` or `CSRF_HEADER_NAME`, use the corresponding cookie name and HTTP header in this configuration. See [client-side setup](/guide/client-side-setup) for complete examples.

## Review partial reloads

Partial reloads now support `except` requests and nested prop paths. A request with a matching `X-Inertia-Partial-Component` header is treated as a partial reload even when it contains only `X-Inertia-Partial-Except`.

For example, the client can request or exclude a nested prop:

```js
router.reload({ only: ["account.plans"] })
router.reload({ except: ["account.token"] })
```

The server returns only metadata for props included in that response. Do not depend on `mergeProps`, `onceProps`, or related fields advertising props that were excluded from a partial reload.

Use `always()` when a prop must be included in every partial response:

```python
from inertia import always, optional

return {
    "currentUser": always(lambda: request.user.username),
    "reports": optional(load_reports),
}
```

## Use v3 server props

### Once props

Once props can use a stable cache key and an expiry. The client will omit an already-cached once prop on later visits unless it is explicitly reloaded.

```python
from datetime import timedelta

from inertia import once

return {
    "plans": once(load_plans, key="billing-plans", expires_at=timedelta(hours=1)),
}
```

Pass `fresh=True` when a once prop must be resolved on every response.

### Merge, deep merge, and scroll props

`merge()` supports append/prepend paths and record matching. `deep_merge()` merges nested objects and lists recursively. `scroll()` supplies the pagination metadata used by Inertia's infinite-scroll components.

```python
from inertia import deep_merge, merge, scroll

return {
    "feed": merge(load_feed, append="items", match_on="items.id"),
    "chat": deep_merge(load_chat, match_on="messages.id"),
    "players": scroll(
        load_players,
        {
            "pageName": "page",
            "previousPage": None,
            "nextPage": 2,
            "currentPage": 1,
        },
        defer=True,
    ),
}
```

Use `defer()` as before for props that should load after the initial page render. It can also be combined with merge, deep-merge, once, matching, and rescue options.

## Use Django messages for flash data

Django messages are automatically included in the page object's top-level `flash.messages` field. Replace props dedicated to one-time notices with Django's standard message API:

```python
from django.contrib import messages
from django.shortcuts import redirect

def update_profile(request):
    # update the profile...
    messages.success(request, "Profile saved!")
    return redirect("profile:show")
```

The client receives:

```json
{
  "flash": {
    "messages": [{"level": "success", "message": "Profile saved!"}]
  }
}
```

## Check redirects and caches

Fragment redirects are sent as `409 Conflict` responses with `X-Inertia-Redirect`, allowing the client to preserve the complete destination URL. Asset-version refreshes apply to `GET` visits only.

All HTML and JSON Inertia responses now vary on `X-Inertia`. Review any reverse-proxy or CDN cache configuration so it honors the `Vary` header.

## Verify the upgrade

- Confirm a full-page visit mounts the v3 client.
- Confirm a form submission sends Django's CSRF header.
- Exercise a nested `only` or `except` reload.
- Confirm flash messages appear once after a redirect.
- Exercise any deferred or infinite-scroll pages in the application.
