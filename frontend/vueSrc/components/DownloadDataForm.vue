<template>
  <q-card class="q-pa-md download-card" bordered>
    <!-- Navigation tabs -->
    <q-card-section class="q-pb-none tab-header">
      <q-tabs
        v-model="activeTab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="static" icon="folder_zip" label="Static Files" />
        <q-tab name="process" icon="settings" label="Process & Download" />
      </q-tabs>
      <q-separator />
    </q-card-section>

    <!-- Tab panels -->
    <q-tab-panels v-model="activeTab" animated class="tab-content">
      <!-- Static Files Panel -->
      <q-tab-panel name="static" class="p-0">
        <lidar-directory-tree />
      </q-tab-panel>

      <!-- Process & Download Panel -->
      <q-tab-panel name="process" class="p-0">
        <process-download-panel />
      </q-tab-panel>
    </q-tab-panels>

    <q-separator class="q-my-md" />
    <q-card-section class="color-selector-section">
      <color-variable-selector />
      <q-separator class="q-my-md" />
      <source-i-d-filter />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref } from "vue";
import ColorVariableSelector from "@/components/ColorVariableSelector.vue";
import LidarDirectoryTree from "@/components/LidarDirectoryTree.vue";
import ProcessDownloadPanel from "@/components/ProcessDownloadPanel.vue";
import SourceIDFilter from "@/components/SourceIDFilter.vue";

const activeTab = ref("static");
</script>

<style scoped>
.download-card {
  position: absolute;
  background: white;
  right: 0;
  top: 0;
  height: 100%;
  width: 500px;
  z-index: 2;
  box-sizing: border-box;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Hide overflow at container level */
  padding: 0; /* Remove padding to maximize space */
  gap: 4rem;
}

.tab-header {
  flex: 0 0 auto; /* Don't grow or shrink */
  padding: 1rem 1rem 0 1rem;
}

.tab-content {
  flex: 1 1 auto; /* Grow and shrink as needed */
  overflow-y: auto; /* Enable scrolling for tab content */
  padding: 0 1rem;
}

.color-selector-section {
  flex: 0 0 auto; /* Don't grow or shrink */
  padding: 1rem;
}

.p-0 {
  padding: 0;
}

/* Ensure tab panels themselves take full height of their container */
:deep(.q-tab-panel) {
  height: 100%;
  overflow-y: auto;
}
</style>
