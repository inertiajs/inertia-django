<script setup lang="ts">
import { router, usePage } from '@inertiajs/vue3'

const page = usePage<Record<string, unknown>>()

function reloadLocale() {
  router.reload({ only: ['config.locale'] })
}
</script>

<template>
  <main>
    <h1>Inertia Django v3 compatibility</h1>
    <pre data-testid="props">{{ JSON.stringify(page.props) }}</pre>
    <button type="button" @click="reloadLocale">Reload locale</button>
  </main>
</template>
