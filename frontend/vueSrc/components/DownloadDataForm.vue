<template>
  <div class="download-panel">
    <q-scroll-area class="fit">
      <div>
        <lidar-directory-tree class="q-mb-sm" />
        <q-separator class="q-mb-sm" />
        <process-download-panel class="q-mb-sm" />
        <q-separator class="q-mb-sm" />
        <color-variable-selector class="q-mb-sm" />
        <q-separator class="q-mb-sm" />
        <source-i-d-filter />
      </div>
    </q-scroll-area>
  </div>
</template>

<script setup lang="ts">
import ColorVariableSelector from "@/components/ColorVariableSelector.vue";
import LidarDirectoryTree from "@/components/LidarDirectoryTree.vue";
import ProcessDownloadPanel from "@/components/ProcessDownloadPanel.vue";
import SourceIDFilter from "@/components/SourceIDFilter.vue";
</script>

<style scoped>
.download-panel {
  position: absolute;
  right: 0;
  top: 0;
  height: 100vh;
  width: 400px;
  max-width: 100%;
  background: white;
  border-left: 1px solid #e0e0e0;
  z-index: 2;
}
</style>
