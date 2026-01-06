<script setup lang="ts">
import { ref, computed } from "vue";
import { useDirectoryStore } from "@/stores/directoryStore";
import { useQuasar } from "quasar";
import FilesPanel from "@/components/pointcloud/panels/FilesPanel.vue";
import ExportPanel from "@/components/pointcloud/panels/ExportPanel.vue";
import DisplayPanel from "@/components/pointcloud/panels/DisplayPanel.vue";
import MissionInfoPanel from "@/components/pointcloud/panels/MissionInfoPanel.vue";

const directoryStore = useDirectoryStore();
const $q = useQuasar();
const activeTab = ref("export");

const tabs = [
  {
    name: "export",
    icon: "file_download",
    label: "Export",
    tooltip:
      "Export and filter point cloud data on-the-fly. Combine filters to reduce file size and focus on specific data.",
    requiresAuth: true,
  },
  {
    name: "files",
    icon: "folder",
    label: "Files",
    tooltip:
      "Browse and manage mission files. Select point cloud data to visualize and work with.",
    requiresAuth: true,
  },
  {
    name: "display",
    icon: "visibility",
    label: "Display",
    tooltip:
      "Customize point cloud visualization. Choose color modes, apply filters, and control display settings.",
    requiresAuth: false,
  },
  {
    name: "info",
    icon: "info",
    label: "Info",
    tooltip:
      "View mission details, point cloud statistics, and metadata. Get comprehensive information about the current mission.",
    requiresAuth: false,
  },
];

// Check if current tab requires authentication
const currentTabRequiresAuth = computed(() => {
  const tab = tabs.find((t) => t.name === activeTab.value);
  return tab?.requiresAuth || false;
});

// Show password banner if mission is protected and current tab requires auth
const showPasswordBanner = computed(() => {
  return (
    directoryStore.isMissionProtected &&
    !directoryStore.isPasswordValid &&
    currentTabRequiresAuth.value
  );
});

// Prompt for password when trying to access protected content
async function promptForPassword() {
  if (!directoryStore.activeMission) return;

  $q.dialog({
    title: "Protected Mission",
    message: `Mission "${directoryStore.activeMission}" is password protected. Please enter the password:`,
    prompt: {
      model: "",
      type: "password",
      isValid: (val: string) => Boolean(val && val.length > 0),
    },
    cancel: true,
    persistent: true,
  }).onOk(async (password: string) => {
    if (!directoryStore.activeMission) return;

    // Validate password
    const isValid = await directoryStore.validatePassword(
      directoryStore.activeMission,
      password,
    );

    if (isValid) {
      directoryStore.setMissionPassword(password);
      $q.notify({
        type: "positive",
        message: "Password accepted. Loading mission data...",
        position: "top",
      });

      // Fetch mission data now that we have valid password
      await directoryStore.fetchMissionData(directoryStore.activeMission);
    } else {
      $q.notify({
        type: "negative",
        message: "Invalid password",
        position: "top",
      });
    }
  });
}
</script>

<template>
  <div class="sidebar-container">
    <!-- Tab Navigation -->
    <q-tabs
      v-model="activeTab"
      active-color="primary"
      indicator-color="primary"
    >
      <q-tab
        v-for="tab in tabs"
        :key="tab.name"
        :name="tab.name"
        :icon="tab.icon"
        :label="tab.label"
        class="text-subtitle2 text-weight-medium"
      >
        <q-tooltip>{{ tab.tooltip }}</q-tooltip>
      </q-tab>
    </q-tabs>

    <q-separator />

    <!-- Tab Panels -->
    <q-scroll-area class="sidebar-content">
      <q-tab-panels v-model="activeTab" animated keep-alive>
        <q-tab-panel name="export" class="q-pa-lg">
          <!-- Show password banner if protected -->
          <div v-if="showPasswordBanner">
            <q-banner class="bg-warning text-white">
              <template v-slot:avatar>
                <q-icon name="lock" size="lg" />
              </template>
              <div class="text-h6 q-mb-sm">Protected Content</div>
              <div class="text-body2 q-mb-md">
                This mission is password protected. Please unlock it to access
                export features.
              </div>
              <q-btn
                outline
                color="white"
                label="Unlock with Password"
                icon="lock_open"
                @click="promptForPassword"
              />
            </q-banner>
          </div>
          <export-panel v-else />
        </q-tab-panel>

        <q-tab-panel name="files" class="q-pa-lg">
          <!-- Show password banner if protected -->
          <div v-if="showPasswordBanner">
            <q-banner class="bg-warning text-white">
              <template v-slot:avatar>
                <q-icon name="lock" size="lg" />
              </template>
              <div class="text-h6 q-mb-sm">Protected Content</div>
              <div class="text-body2 q-mb-md">
                This mission is password protected. Please unlock it to browse
                mission files.
              </div>
              <q-btn
                outline
                color="white"
                label="Unlock with Password"
                icon="lock_open"
                @click="promptForPassword"
              />
            </q-banner>
          </div>
          <files-panel v-else />
        </q-tab-panel>

        <q-tab-panel name="display" class="q-pa-lg">
          <display-panel />
        </q-tab-panel>

        <q-tab-panel name="info" class="q-pa-lg">
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
