# Client-side setup

::: tip
If you used the [template based setup](/guide/server-side-setup.md#template-based-setup), you can skip client-side setup.
It is already configured as part of the template based setup.
:::

Once you have [server-side configured](/guide/server-side-setup.md), you then need to setup your client-side framework. Inertia currently provides support for React, Vue, and Svelte.

## Install dependencies

First, install the Inertia client-side adapter corresponding to your framework of choice.

::: code-group

```shell [Vue]
npm install @inertiajs/vue3 vue @vitejs/plugin-vue
```

```shell [React]
npm install @inertiajs/react react react-dom @vitejs/plugin-react
```

```shell [Svelte 4, Svelte 5]
npm install @inertiajs/svelte svelte @sveltejs/vite-plugin-svelte
```

:::

## Configure Vite

Create a `vite.config.js` file in your root directory and configure it for use with your frontend of choice and  `django-vite`.

::: code-group

```js [Vue]
// vite.config.js
import { join, resolve } from "node:path";
import vue from "@vitejs/plugin-vue";
import { defineConfig, loadEnv } from "vite";


export default defineConfig((mode) => {
  const env = loadEnv(mode, process.cwd(), "");

  const INPUT_DIR = "./frontend";
  const OUTPUT_DIR = "./frontend/dist";

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        "@": resolve(INPUT_DIR),
        vue: "vue/dist/vue.esm-bundler.js",
      },
    },
    root: resolve(INPUT_DIR),
    base: "/static/",
    server: {
      host: "0.0.0.0",
      port: env.DJANGO_VITE_DEV_SERVER_PORT || 5173,
      watch: {
        usePolling: true,
      },
    },
    build: {
      manifest: "manifest.json",
      emptyOutDir: true,
      outDir: resolve(OUTPUT_DIR),
      rollupOptions: {
        input: {
          main: join(INPUT_DIR, "/js/main.js"),
          css: join(INPUT_DIR, "/css/main.css"),
        },
      },
    },
  };
});

```

```js [React]
// vite.config.js
import { join, resolve } from "node:path";
import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv } from "vite";


export default defineConfig((mode) => {
	const env = loadEnv(mode, process.cwd(), "");

	const INPUT_DIR = "./frontend";
	const OUTPUT_DIR = "./frontend/dist";

	return {
		plugins: [react()],
		resolve: {
			alias: {
				"@": resolve(INPUT_DIR),
			},
		},
		root: resolve(INPUT_DIR),
		base: "/static/",
		server: {
			host: "0.0.0.0",
			port: env.DJANGO_VITE_DEV_SERVER_PORT || 5173,
			watch: {
				usePolling: true,
			},
		},
		build: {
			manifest: "manifest.json",
			emptyOutDir: true,
			outDir: resolve(OUTPUT_DIR),
			rollupOptions: {
				input: {
					main: join(INPUT_DIR, "/js/main.js"),
					css: join(INPUT_DIR, "/css/main.css"),
				},
			},
		},
	};
});
```

```js [Svelte]
// vite.config.js
import { join, resolve } from "node:path";
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig, loadEnv } from "vite";


export default defineConfig((mode) => {
	const env = loadEnv(mode, process.cwd(), "");

	const INPUT_DIR = "./frontend";
	const OUTPUT_DIR = "./frontend/dist";

	return {
		plugins: [svelte()],
		resolve: {
			alias: {
				"@": resolve(INPUT_DIR),
			},
		},
		root: resolve(INPUT_DIR),
		base: "/static/",
		server: {
			host: "0.0.0.0",
			port: env.DJANGO_VITE_DEV_SERVER_PORT || 5173,
			watch: {
				usePolling: true,
			},
		},
		build: {
			manifest: "manifest.json",
			emptyOutDir: true,
			outDir: resolve(OUTPUT_DIR),
			rollupOptions: {
				input: {
					main: join(INPUT_DIR, "/js/main.js"),
					css: join(INPUT_DIR, "/css/main.css"),
				},
			},
		},
	};
});
```
:::

## Initialize the Inertia app

Create a `frontend` directory in your root directory and add a `js` directory inside it.
Inside the `js` directory, create a `main.js` file.

Next, update your main JavaScript file (`main.js`) to boot your Inertia app.
To accomplish this, we'll initialize the client-side framework with the base Inertia component.

We will also configure CSRF to work properly with Django.

::: code-group

```js [Vue]
// frontend/js/main.js
import { createApp, h } from "vue";
import { createInertiaApp } from "@inertiajs/vue3";
import axios from "axios";

document.addEventListener("DOMContentLoaded", () => {
	axios.defaults.xsrfCookieName = "csrftoken";
	axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

    createInertiaApp({
        resolve: (name) => {
            const pages = import.meta.glob("../pages/**/*.vue", { eager: true });
            return pages[`../pages/${name}.vue`];
        },
        setup({ el, App, props, plugin }) {
            createApp({ render: () => h(App, props) })
                .use(plugin)
                .mount(el);
        },
    });
});
```

```js [React]
// frontend/js/main.js
import { createInertiaApp } from "@inertiajs/react";
import { createElement } from "react";
import { createRoot } from "react-dom/client";

import axios from "axios";

document.addEventListener("DOMContentLoaded", () => {
	axios.defaults.xsrfCookieName = "csrftoken";
	axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

    createInertiaApp({
        resolve: (name) => {
            const pages = import.meta.glob("../pages/**/*.jsx", { eager: true });
            return pages[`../pages/${name}.jsx`];
        },
        setup({ el, App, props }) {
            const root = createRoot(el);
            root.render(createElement(App, props));
        },
    });
});
```

```js [Svelte 4]
// frontend/js/main.js
import { createInertiaApp } from "@inertiajs/svelte";
import axios from "axios";

document.addEventListener("DOMContentLoaded", () => {
	axios.defaults.xsrfCookieName = "csrftoken";
	axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

    createInertiaApp({
        resolve: (name) => {
            const pages = import.meta.glob("../pages/**/*.svelte", { eager: true });
            return pages[`../pages/${name}.svelte`];
        },
        setup({ el, App, props }) {
            new App({ target: el, props });
        },
    });
});
```

```js [Svelte 5]
// frontend/js/main.js
import { createInertiaApp } from "@inertiajs/svelte";
import { mount } from "svelte";

createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("./Pages/**/*.svelte", { eager: true });
        return pages[`./Pages/${name}.svelte`];
    },
    setup({ el, App, props }) {
        mount(App, { target: el, props });
    },
});
```

:::

The `setup` callback receives everything necessary to initialize the client-side framework, including the root Inertia `App` component.

# Resolving components

The `resolve` callback tells Inertia how to load a page component. It receives a page name (string), and returns a page component module. How you implement this callback depends on which bundler (Vite or Webpack) you're using.

::: code-group

```js [Vue]
// frontend/js/main.js
createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("../pages/**/*.vue", { eager: true });
        return pages[`../pages/${name}.vue`];
    },
    // ...
});
```

```js [React]
// frontend/js/main.js
createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("../pages/**/*.jsx", { eager: true });
        return pages[`../pages/${name}.jsx`];
    },
    //...
});
```

```js [Svelte 4, Svelte 5]
// frontend/js/main.js
createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("../pages/**/*.svelte", { eager: true });
        return pages[`../pages/${name}.svelte`];
    },
    //...
});
```

:::

By default we recommend eager loading your components, which will result in a single JavaScript bundle. However, if you'd like to lazy-load your components, see our [code splitting](/guide/code-splitting.md) documentation.

## Defining a root element

By default, Inertia assumes that your application's root template has a root element with an `id` of `app`.
This is already configured if you use the `{% block inertia %} {% endblock %}` template tag from `inertia-django` in your base html template.

If your application's root element has a different `id`, you can provide it using the `id` property.

```js
createInertiaApp({
    id: "my-app",
    // ...
});
```
