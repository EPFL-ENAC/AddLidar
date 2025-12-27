<script setup lang="ts">
import { ref } from "vue";
import FilesPanel from "@/components/pointcloud/panels/FilesPanel.vue";
import ExportPanel from "@/components/pointcloud/panels/ExportPanel.vue";
import JobsPanel from "@/components/pointcloud/panels/JobsPanel.vue";
import AppearancePanel from "@/components/pointcloud/panels/AppearancePanel.vue";
import FiltersPanel from "@/components/pointcloud/panels/FiltersPanel.vue";

const activeTab = ref("export");

const tabs = [
  { name: "export", icon: "file_download", label: "Export" },
  { name: "jobs", icon: "history", label: "Jobs" },
  { name: "files", icon: "folder", label: "Files" },
  { name: "appearance", icon: "palette", label: "Color" },
  { name: "filters", icon: "filter_list", label: "Filters" },
];
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
      />
    </q-tabs>

    <q-separator />

    <!-- Tab Panels -->
    <q-scroll-area class="sidebar-content">
      <q-tab-panels v-model="activeTab" animated keep-alive>
        <q-tab-panel name="export" class="q-pa-none">
          <export-panel />
        </q-tab-panel>

        <q-tab-panel name="jobs" class="q-pa-none">
          <jobs-panel />
        </q-tab-panel>

        <q-tab-panel name="files" class="q-pa-none">
          <files-panel />
        </q-tab-panel>

        <q-tab-panel name="appearance" class="q-pa-none">
          <appearance-panel />
        </q-tab-panel>

        <q-tab-panel name="filters" class="q-pa-none">
          <filters-panel />
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
