<script setup lang="ts">
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

defineProps<{
  missionName?: string;
}>();

const router = useRouter();
const sidebarOpen = ref(true);
const currentRoute = computed(() => router.currentRoute.value.path);

const navItems = [
  { label: "Missions", to: "/", icon: "explore" },
  { label: "About", to: "/about", icon: "info" },
];
</script>

<template>
  <q-layout view="hHh lpR fFf">
    <!-- App Header -->
    <q-header class="app-header bg-white text-dark">
      <q-toolbar>
        <q-btn flat round icon="arrow_back" @click="router.push('/')" />

        <q-toolbar-title class="row items-center gap-sm">
          <q-icon name="terrain" color="primary" size="28px" />
          <span class="text-weight-medium">AddLidar</span>
          <q-separator vertical class="q-mx-sm" />
          <span class="text-body2 text-grey-7">{{ missionName }}</span>
        </q-toolbar-title>

        <q-tabs
          :model-value="currentRoute"
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

        <q-btn
          flat
          round
          :icon="sidebarOpen ? 'menu_open' : 'menu'"
          @click="sidebarOpen = !sidebarOpen"
        >
          <q-tooltip>{{ sidebarOpen ? "Hide" : "Show" }} sidebar</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <!-- Main Content -->
    <q-page-container>
      <q-page class="viewer-page">
        <div class="viewer-content">
          <!-- Viewer Canvas -->
          <div class="viewer-canvas">
            <slot name="viewer" />
          </div>

          <!-- Sidebar -->
          <transition name="slide-right">
            <aside v-show="sidebarOpen" class="app-sidebar">
              <slot name="sidebar" />
            </aside>
          </transition>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<style scoped>
.viewer-page {
  height: calc(100vh - var(--header-height, 56px));
  padding: 0;
}

.viewer-content {
  display: flex;
  height: 100%;
}

.viewer-canvas {
  flex: 1;
  position: relative;
  min-width: 0;
}
</style>
