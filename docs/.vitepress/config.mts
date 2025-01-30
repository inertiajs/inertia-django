import { defineConfig } from "vitepress";

const title = "Inertia.js Django";
const description = "Build single page apps, without building an API";
const site = "https://inertiajs.com";
const image = `${site}/og_image.png`; // TODO: update this

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: "Inertia.js Django",
    description: "Build single page apps, without building an API",

    cleanUrls: true,

    head: [
        ["link", { rel: "icon", href: "/favicon.ico", sizes: "32x32" }],
        ["link", { rel: "icon", href: "/icon.svg", type: "image/svg+xml" }],

        ["meta", { name: "twitter:card", content: "summary_large_image" }],
        ["meta", { name: "twitter:site", content: site }],
        ["meta", { name: "twitter:description", value: description }],
        ["meta", { name: "twitter:image", content: image }],

        ["meta", { property: "og:type", content: "website" }],
        ["meta", { property: "og:locale", content: "en_US" }],
        ["meta", { property: "og:site", content: site }],
        ["meta", { property: "og:site_name", content: title }],
        ["meta", { property: "og:image", content: image }],
        ["meta", { property: "og:description", content: description }],
    ],

    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        nav: [
            { text: "Home", link: "/" },
            { text: "Guide", link: "/guide" },
            {
                text: "Links",
                items: [
                    {
                        text: "Official Inertia.js docs",
                        link: "https://inertiajs.com",
                    },
                    {
                        text: "inertia-django on PyPI",
                        link: "https://pypi.org/project/inertia-django",
                    },
                ],
            },
        ],

        sidebar: {
            "/guide/": [
                {
                    items: [{ text: "Introduction", link: "/guide" }],
                },
                {
                    text: "Core concepts",
                    items: [
                        { text: "Who is it for", link: "/guide/who-is-it-for" },
                        { text: "How it works", link: "/guide/how-it-works" },
                        { text: "The protocol", link: "/guide/the-protocol" },
                    ],
                },
                {
                    text: "The basics",
                    items: [{ text: "Links", link: "/guide/links" }],
                },
            ],
        },

        socialLinks: [
            {
                icon: "github",
                link: "https://github.com/inertiajs/inertia-django",
            },
        ],
    },
});
