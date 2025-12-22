<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

interface NavItem {
  label: string;
  to: string;
  icon?: string;
}

const navItems: NavItem[] = [
  { label: "Missions", to: "/", icon: "explore" },
  { label: "About", to: "/about", icon: "info" },
];

const currentRoute = computed(() => router.currentRoute.value.path);
</script>

<template>
  <q-layout view="hHh lpR fFf">
    <q-header class="app-header bg-white text-dark">
      <q-toolbar>
        <q-toolbar-title class="row items-center gap-sm">
          <q-icon name="terrain" color="primary" size="28px" />
          <span class="text-weight-medium">AddLidar</span>
        </q-toolbar-title>

        <q-tabs
          v-model="currentRoute"
          inline-label
          class="text-grey-8"
          active-color="primary"
          indicator-color="primary"
        >
          <q-route-tab
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            :icon="item.icon"
            :label="item.label"
          />
        </q-tabs>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <slot />
    </q-page-container>
  </q-layout>
</template>
