import { createInertiaApp } from '@inertiajs/vue3'
import { createApp, h } from 'vue'
import TestComponent from './pages/TestComponent.vue'

createInertiaApp({
  resolve: () => TestComponent,
  setup({ el, App, props, plugin }) {
    createApp({ render: () => h(App, props) }).use(plugin).mount(el)
  },
  http: {
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: 'X-CSRFToken',
  },
})
