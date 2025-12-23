<script setup lang="ts">
import { ref } from "vue";
import EPFLLogo from "@/assets/EPFL_Logo.svg";

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

const showAbout = ref(false);

function handleBack() {
  emit("back");
}

function toggleAbout() {
  showAbout.value = !showAbout.value;
}
</script>

<template>
  <div
    class="relative-position overflow-hidden"
    style="height: 100vh; width: 100vw"
  >
    <!-- Right Panel (Full Background) -->
    <main class="absolute-full bg-grey-2">
      <slot name="content" />
    </main>

    <!-- Left Sidebar (Floating) -->
    <aside class="absolute column bg-white sidebar-floating">
      <!-- Header -->
      <header
        class="q-pa-md"
        style="border-bottom: 1px solid rgba(0, 0, 0, 0.06)"
      >
        <div class="row items-center justify-between">
          <q-btn
            flat
            round
            dense
            icon="arrow_back"
            color="grey-8"
            size="sm"
            :style="{ visibility: showBackButton ? 'visible' : 'hidden' }"
            @click="handleBack"
          >
            <q-tooltip v-if="showBackButton">Back to missions</q-tooltip>
          </q-btn>

          <div class="col row items-center justify-center q-gutter-sm q-pa-md">
            <img :src="EPFLLogo" alt="EPFL" style="height: 24px; width: auto" />
            <q-separator vertical inset />
            <div class="row items-center q-gutter-xs">
              <q-icon name="terrain" color="primary" size="20px" />
              <span class="text-h6 text-weight-medium">AddLidar</span>
            </div>
          </div>

          <q-btn
            flat
            round
            dense
            :icon="showAbout ? 'close' : 'info_outline'"
            color="grey-8"
            size="sm"
            @click="toggleAbout"
          >
            <q-tooltip>{{ showAbout ? "Close" : "About" }}</q-tooltip>
          </q-btn>
        </div>
      </header>

      <!-- Sidebar Content -->
      <div class="col overflow-hidden column">
        <div v-if="showAbout" class="column q-pa-lg">
          <div class="text-center q-mb-md">
            <q-icon
              name="terrain"
              color="primary"
              size="64px"
              class="q-mb-md"
            />
            <h2 class="text-h5 text-weight-medium q-mb-sm">About AddLidar</h2>
          </div>

          <p class="text-body2 text-grey-7 q-mb-md">
            AddLidar is a web application for exploring and visualizing LiDAR
            point cloud data. Browse available missions, visualize point clouds
            in 3D, and export subsets of data in various formats.
          </p>

          <div class="column q-gutter-md q-mb-lg">
            <div class="row items-center q-gutter-sm">
              <q-icon name="explore" size="24px" color="primary" />
              <div class="col">
                <div class="text-weight-medium">Browse Missions</div>
                <div class="text-caption text-grey-6">
                  View and select from available LiDAR missions
                </div>
              </div>
            </div>
            <div class="row items-center q-gutter-sm">
              <q-icon name="map" size="24px" color="primary" />
              <div class="col">
                <div class="text-weight-medium">Interactive Map</div>
                <div class="text-caption text-grey-6">
                  Visualize mission footprints geographically
                </div>
              </div>
            </div>
            <div class="row items-center q-gutter-sm">
              <q-icon name="3d_rotation" size="24px" color="primary" />
              <div class="col">
                <div class="text-weight-medium">3D Viewer</div>
                <div class="text-caption text-grey-6">
                  Explore point clouds in real-time 3D
                </div>
              </div>
            </div>
            <div class="row items-center q-gutter-sm">
              <q-icon name="download" size="24px" color="primary" />
              <div class="col">
                <div class="text-weight-medium">Export Data</div>
                <div class="text-caption text-grey-6">
                  Download selected regions in multiple formats
                </div>
              </div>
            </div>
          </div>

          <q-separator class="q-my-md" />

          <div class="text-caption text-grey-5 text-center">
            Developed by EPFL-ENAC
          </div>
        </div>
        <template v-else>
          <!-- Mission Name Title -->
          <div v-if="subtitle" class="q-px-lg q-pt-md q-pb-sm">
            <div class="row items-center q-my-md justify-between">
              <div
                class="text-overline text-grey-6"
                style="letter-spacing: 0.5px"
              >
                SELECTED MISSION
              </div>
              <div class="text-h6 text-weight-medium ellipsis">
                {{ subtitle }}
              </div>
            </div>
          </div>

          <q-separator v-if="subtitle" />

          <slot name="sidebar" />
        </template>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.sidebar-floating {
  top: 20px;
  left: 20px;
  bottom: 20px;
  width: 30%;
  min-width: 550px;
  max-width: 600px;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

@media (max-width: 1024px) {
  .sidebar-floating {
    width: 40%;
    min-width: 400px;
  }
}

@media (max-width: 768px) {
  .sidebar-floating {
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    min-width: 0;
    max-width: none;
    height: 50%;
    border-radius: 12px 12px 0 0;
  }
}
</style>
