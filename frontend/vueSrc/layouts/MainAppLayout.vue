<script setup lang="ts">
import { ref, computed } from "vue";
import { useQuasar } from "quasar";

interface Props {
  showBackButton?: boolean;
  subtitle?: string;
}

const props = withDefaults(defineProps<Props>(), {
  showBackButton: false,
});

const emit = defineEmits<{
  back: [];
}>();

const $q = useQuasar();
const leftDrawerOpen = ref(true);

const drawerWidth = computed(() => {
  if ($q.screen.lt.sm) return $q.screen.width; // Full width on mobile
  if ($q.screen.lt.md) return 400;
  if ($q.screen.lt.lg) return 450;
  if ($q.screen.lt.xl) return 500;
  return 650; // 650px on large screens
});

function handleBack() {
  emit("back");
}

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>

<template>
  <q-layout view="lHh LpR lFf" style="height: 100vh">
    <!-- Left Drawer -->
    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      :width="drawerWidth"
      :breakpoint="768"
      bordered
      class="bg-white drawer-custom"
    >
      <div class="column full-height">
        <!-- Header -->
        <header class="q-px-md q-px-lg-lg q-py-lg q-py-lg-lg q-py-xl-xl">
          <div class="row items-center justify-between">
            <div class="row items-center q-gutter-xs">
              <q-btn
                flat
                round
                dense
                icon="arrow_back"
                color="grey-8"
                size="md"
                :style="{ visibility: showBackButton ? 'visible' : 'hidden' }"
                @click="handleBack"
              >
                <q-tooltip v-if="showBackButton">Back to missions</q-tooltip>
              </q-btn>
            </div>

            <div class="col row items-center justify-center q-px-xs">
              <div class="row items-center">
                <q-icon
                  name="view_in_ar"
                  color="black"
                  size="26px"
                  class="q-mr-xs"
                />
                <span class="text-h6">AddLidar</span>
              </div>
              <q-separator vertical size="2px" inset class="q-mx-md" />
              <img
                src="@/assets/EPFL_Logo.svg"
                alt="EPFL"
                style="height: 20px; width: auto"
              />
            </div>

            <!-- Fake spacer to balance the left side and center the middle content -->
            <div
              class="row items-center q-gutter-xs"
              style="visibility: hidden"
            >
              <q-btn flat round dense icon="arrow_back" size="md" />
            </div>
          </div>
        </header>

        <!-- Sidebar Content -->
        <div class="col overflow-auto column sidebar-scrollable">
          <slot name="sidebar" />
        </div>
      </div>
    </q-drawer>

    <!-- Floating Toggle Button (outside drawer so it's always visible) -->
    <q-btn
      :icon="leftDrawerOpen ? 'menu_open' : 'menu'"
      color="primary"
      round
      unelevated
      size="md"
      class="drawer-edge-toggle"
      :style="{ left: leftDrawerOpen ? `${drawerWidth - 20}px` : '16px' }"
      @click="toggleLeftDrawer"
    >
      <q-tooltip>{{ leftDrawerOpen ? "Close" : "Open" }} sidebar</q-tooltip>
    </q-btn>

    <!-- Main Content -->
    <q-page-container>
      <q-page class="bg-grey-2">
        <div class="content-wrapper">
          <slot name="content" />
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<style scoped>
/* Modern minimalist scrollbar */
.sidebar-scrollable {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
  min-height: 0;
}

.sidebar-scrollable::-webkit-scrollbar {
  width: 6px;
}

.sidebar-scrollable::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-scrollable::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.sidebar-scrollable::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

.q-page {
  min-height: 100vh;
  position: relative;
}

.content-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
}

.drawer-custom {
  max-width: 100vw;
  overflow-x: hidden;
}

.drawer-custom :deep(*) {
  max-width: 100%;
  overflow-x: hidden;
}

.drawer-edge-toggle {
  position: fixed;
  top: 2.3rem;
  transform: translateY(-50%);
  z-index: 3000;
  transition: left 0.15s ease;
}

/* Mobile: button inside drawer */
@media (max-width: 600px) {
  .drawer-edge-toggle {
    right: 16px !important;
    left: auto !important;
  }
}

/* Remove conflicting media queries - width is now controlled by computed property */
</style>
