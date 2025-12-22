<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import AppToolbar from "@/components/AppToolbar.vue";

defineProps<{
  missionName?: string;
}>();

const router = useRouter();
const sidebarOpen = ref(true);
</script>

<template>
  <q-layout view="hHh lpR fFf">
    <AppToolbar
      show-back-button
      :subtitle="missionName"
      show-sidebar-toggle
      :sidebar-open="sidebarOpen"
      @back="router.push('/')"
      @toggle-sidebar="sidebarOpen = !sidebarOpen"
    />

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
