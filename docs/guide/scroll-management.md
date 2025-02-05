# Scroll management

## Scroll resetting

When navigating between pages, Inertia mimics default browser behavior by automatically resetting the scroll position of the document body (as well as any [scroll regions](#scroll-regions) you've defined) back to the top.

In addition, Inertia keeps track of the scroll position of each page and automatically restores that scroll position as you navigate forward and back in history.

## Scroll preservation

Sometimes it's desirable to prevent the default scroll resetting when making visits. You can disable this behaviour by setting the `preserveScroll` option to `false`.

::: code-group

```js [Vue]
import { router } from "@inertiajs/vue3";

router.visit(url, { preserveScroll: false });
```

```js [React]
import { router } from "@inertiajs/react";

router.visit(url, { preserveScroll: false });
```

```js [Svelte 4, Svelte 5]
import { router } from "@inertiajs/svelte";

router.visit(url, { preserveScroll: false });
```

:::

If you'd like to only preserve the scroll position if the response includes validation errors, set the `preserveScroll` option to `"errors"`.

::: code-group

```js [Vue]
import { router } from "@inertiajs/vue3";

router.visit(url, { preserveScroll: "errors" });
```

```js [React]
import { router } from "@inertiajs/react";

router.visit(url, { preserveScroll: "errors" });
```

```js [Svelte 4, Svelte 5]
import { router } from "@inertiajs/svelte";

router.visit(url, { preserveScroll: "errors" });
```

:::

You can also lazily evaluate the `preserveScroll` option based on the response by providing a callback.

::: code-group

```js [Vue]
import { router } from "@inertiajs/vue3";

router.post("/users", data, {
    preserveScroll: (page) => page.props.someProp === "value",
});
```

```js [React]
import { router } from "@inertiajs/react";

router.post("/users", data, {
    preserveScroll: (page) => page.props.someProp === "value",
});
```

```js [Svelte 4, Svelte 5]
import { router } from "@inertiajs/svelte";

router.post("/users", data, {
    preserveScroll: (page) => page.props.someProp === "value",
});
```

:::

When using an [Inertia link](/guide/links), you can preserve the scroll position using the `preserveScroll` prop.

::: code-group

```vue [Vue]
<script setup>
import { Link } from "@inertiajs/vue3";
</script>

<template>
    <Link href="/" preserve-scroll>Home</Link>
</template>
```

```jsx [React]
import { Link } from "@inertiajs/react";

export default () => (
    <Link href="/" preserveScroll>
        Home
    </Link>
);
```

```svelte [Svelte 4, Svelte 5]
<script>
  import { inertia, Link } from '@inertiajs/svelte'
</script>

<a href="/" use:inertia={{ preserveScroll: true }}>Home</a>

<Link href="/" preserveScroll>Home</Link>
```

:::

## Scroll regions

If your app doesn't use document body scrolling, but instead has scrollable elements (using the `overflow` CSS property), scroll resetting will not work.

In these situations, you must tell Inertia which scrollable elements to manage by adding the `scroll-region` attribute to the element.

```html
<div class="overflow-y-auto" scroll-region>
    <!-- Your page content -->
</div>
```
