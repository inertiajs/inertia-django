# Code splitting

Code splitting breaks apart the various pages of your application into smaller bundles, which are then loaded on demand when visiting new pages. This can significantly reduce the size of the initial JavaScript bundle loaded by the browser, improving the time to first render.

While code splitting is helpful for very large projects, it does require extra requests when visiting new pages. Generally speaking, if you're able to use a single bundle, your app is going to feel snappier.

To enable code splitting you'll need to tweak the resolve callback in your `createInertiaApp()` configuration, and how you do this is different depending on which bundler you're using.

## Using Vite

Vite enables code splitting (or lazy-loading as they call it) by default when using their `import.meta.glob()` function, so simply omit the `{ eager: true }` option, or set it to false, to disable eager loading.

::: code-group

```js [Vue]
// frontend/entrypoints/inertia.js
createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("../pages/**/*.vue", { eager: true }); // [!code --]
        return pages[`../pages/${name}.vue`]; // [!code --]
        const pages = import.meta.glob("../pages/**/*.vue"); // [!code ++]
        return pages[`../pages/${name}.vue`](); // [!code ++]
    },
    //...
});
```

```js [React]
// frontend/entrypoints/inertia.js
createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("../pages/**/*.jsx", { eager: true }); // [!code --]
        return pages[`../pages/${name}.jsx`]; // [!code --]
        const pages = import.meta.glob("../pages/**/*.jsx"); // [!code ++]
        return pages[`../pages/${name}.jsx`](); // [!code ++]
    },
    //...
});
```

```js [Svelte 4, Svelte 5]
// frontend/entrypoints/inertia.js
createInertiaApp({
    resolve: (name) => {
        const pages = import.meta.glob("../pages/**/*.svelte", { eager: true }); // [!code --]
        return pages[`../pages/${name}.svelte`]; // [!code --]
        const pages = import.meta.glob("../pages/**/*.svelte"); // [!code ++]
        return pages[`../pages/${name}.svelte`](); // [!code ++]
    },
    //...
});
```

:::
