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
  <div class="row overflow-hidden" style="height: 100vh; width: 100vw">
    <!-- Left Sidebar -->
    <aside
      class="column bg-white sidebar-width"
      style="border-right: 1px solid #e0e0e0"
    >
      <!-- Header -->
      <header
        class="q-pa-md"
        style="border-bottom: 1px solid rgba(0, 0, 0, 0.06)"
      >
        <div class="row items-center justify-between">
          <q-btn
            v-if="showBackButton"
            flat
            round
            dense
            icon="arrow_back"
            color="grey-8"
            size="sm"
            @click="handleBack"
          >
            <q-tooltip>Back to missions</q-tooltip>
          </q-btn>

          <div class="col row items-center justify-center q-gutter-sm">
            <img :src="EPFLLogo" alt="EPFL" style="height: 24px; width: auto" />
            <q-separator vertical inset />
            <div class="column items-center">
              <div class="row items-center q-gutter-xs">
                <q-icon name="terrain" color="primary" size="20px" />
                <span class="text-h6 text-weight-medium">AddLidar</span>
              </div>
              <div v-if="subtitle" class="text-caption text-grey-7 ellipsis">
                {{ subtitle }}
              </div>
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
        <slot v-else name="sidebar" />
      </div>
    </aside>

    <!-- Right Panel -->
    <main class="col relative-position bg-grey-2">
      <slot name="content" />
    </main>
  </div>
</template>

<style scoped>
.sidebar-width {
  width: 30%;
  min-width: 500px;
  max-width: 600px;
}

@media (max-width: 1024px) {
  .sidebar-width {
    width: 35%;
    min-width: 350px;
  }
}

@media (max-width: 768px) {
  .sidebar-width {
    width: 100%;
    min-width: 0;
    max-width: none;
    height: 40%;
    border-right: none !important;
    border-bottom: 1px solid #e0e0e0;
  }
}
</style>
