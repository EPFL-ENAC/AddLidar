<script setup lang="ts">
import AppToolbar from "@/components/AppToolbar.vue";
</script>

<template>
  <q-layout view="hHh lpR fFf">
    <AppToolbar />

    <q-page-container>
      <slot />
    </q-page-container>
  </q-layout>
</template>
