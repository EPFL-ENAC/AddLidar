<script setup lang="ts">
import { ref } from 'vue'
import FilesPanel from '@/components/pointcloud/panels/FilesPanel.vue'
import ExportPanel from '@/components/pointcloud/panels/ExportPanel.vue'
import DisplayPanel from '@/components/pointcloud/panels/DisplayPanel.vue'
import MissionInfoPanel from '@/components/pointcloud/panels/MissionInfoPanel.vue'

const activeTab = ref('export')

const tabs = [
  {
    name: 'export',
    icon: 'file_download',
    label: 'Export',
    tooltip:
      'Export and filter point cloud data on-the-fly. Combine filters to reduce file size and focus on specific data.',
  },
  {
    name: 'files',
    icon: 'folder',
    label: 'Files',
    tooltip:
      'Browse and manage mission files. Select point cloud data to visualize and work with.',
  },
  {
    name: 'display',
    icon: 'visibility',
    label: 'Display',
    tooltip:
      'Customize point cloud visualization. Choose color modes, apply filters, and control display settings.',
  },
  {
    name: 'info',
    icon: 'info',
    label: 'Info',
    tooltip:
      'View mission details, point cloud statistics, and metadata. Get comprehensive information about the current mission.',
  },
]
</script>

<template>
  <div class="sidebar-container">
    <!-- Tab Navigation -->
    <q-tabs
      v-model="activeTab"
      class="text-grey-7"
      active-color="primary"
      indicator-color="primary"
    >
      <q-tab
        v-for="tab in tabs"
        :key="tab.name"
        :name="tab.name"
        :icon="tab.icon"
        :label="tab.label"
      >
        <q-tooltip>{{ tab.tooltip }}</q-tooltip>
      </q-tab>
    </q-tabs>

    <q-separator />

    <!-- Tab Panels -->
    <q-scroll-area class="sidebar-content q-pa-lg">
      <q-tab-panels v-model="activeTab" animated keep-alive>
        <q-tab-panel name="export" class="q-pa-none">
          <export-panel />
        </q-tab-panel>

        <q-tab-panel name="files" class="q-pa-none">
          <files-panel />
        </q-tab-panel>

        <q-tab-panel name="display" class="q-pa-none">
          <display-panel />
        </q-tab-panel>
        <q-tab-panel name="info" class="q-pa-none">
          <mission-info-panel />
        </q-tab-panel>
      </q-tab-panels>
    </q-scroll-area>
  </div>
</template>

<style scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.sidebar-content {
  flex: 1;
}
</style>
