<template>
  <div class="directory-tree-container">
    <!-- Search filter -->
    <q-input
      v-model="searchTerm"
      outlined
      dense
      label="Search files"
      class="q-mb-md"
      clearable
    >
      <template v-slot:append>
        <q-icon name="search" />
      </template>
    </q-input>

    <div v-if="isLoading" class="text-center q-pa-md">
      <q-spinner color="primary" size="24px" />
      <div class="q-mt-sm text-grey">Loading mission data...</div>
    </div>

    <div v-else-if="error" class="text-center q-pa-md text-negative">
      <q-icon name="error" size="24px" />
      <div class="q-mt-sm">{{ error }}</div>
    </div>

    <div v-else-if="!activeMission" class="text-center q-pa-md">
      <q-icon name="folder_off" size="24px" />
      <div class="q-mt-sm text-grey">No mission selected</div>
    </div>

    <!-- Files in active mission -->
    <q-list v-else bordered separator class="rounded-borders list-files">
      <q-item class="bg-primary text-white">
        <q-item-section>
          <q-item-label>
            <q-icon name="folder" class="q-mr-sm" />
            {{ activeMission }}
          </q-item-label>
        </q-item-section>
      </q-item>

      <q-item
        v-for="item in filteredFiles"
        :key="item.folder_key"
        clickable
        :class="{ 'has-files': item.file_count > 0 }"
      >
        <q-item-section>
          <q-item-label>{{ getFolderName(item.folder_key) }}</q-item-label>
          <q-item-label caption>
            {{ formatSize(item.size_kb) }} ·
            {{ formatDate(item.last_processed) }}
            <q-badge
              v-if="item.file_count > 0"
              color="green"
              text-color="white"
              class="q-ml-xs"
            >
              {{ item.file_count }}
              {{ item.file_count === 1 ? "file" : "files" }}
            </q-badge>
            <q-badge v-else color="grey" text-color="white" class="q-ml-xs"
              >Empty</q-badge
            >
          </q-item-label>
        </q-item-section>

        <q-item-section side v-if="item.file_count > 0">
          <q-btn
            flat
            round
            dense
            icon="download"
            color="primary"
            @click="downloadArchive(item.output_path)"
          >
            <q-tooltip>Download archive</q-tooltip>
          </q-btn>
        </q-item-section>
      </q-item>

      <q-item v-if="!filteredFiles.length">
        <q-item-section class="text-center text-grey">
          No folders found
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useDirectoryStore } from "@/stores/directoryStore";

// Get store
const directoryStore = useDirectoryStore();
const searchTerm = ref("");

// Computed properties from store
const directoryData = computed(() => directoryStore.directoryData);
const isLoading = computed(() => directoryStore.isLoading);
const error = computed(() => directoryStore.error);
const activeMission = computed(() => directoryStore.activeMission);

// Filter files based on search term
const filteredFiles = computed(() => {
  if (!directoryData.value.length) {
    return [];
  }

  let files = directoryData.value;

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    files = files.filter(
      (item) =>
        getFolderName(item.folder_key).toLowerCase().includes(term) ||
        item.folder_key.toLowerCase().includes(term),
    );
  }

  // Sort by folder name
  return files.sort((a, b) => {
    const aName = getFolderName(a.folder_key);
    const bName = getFolderName(b.folder_key);
    return aName.localeCompare(bName);
  });
});

// Format size to human-readable
function formatSize(sizeKb: number): string {
  if (sizeKb === 0) {
    return "0 KB";
  }
  if (sizeKb < 1024) {
    return `${sizeKb} KB`;
  } else if (sizeKb < 1024 * 1024) {
    return `${(sizeKb / 1024).toFixed(2)} MB`;
  } else {
    return `${(sizeKb / (1024 * 1024)).toFixed(2)} GB`;
  }
}

// Format date to human-readable
function formatDate(dateStr: number | null): string {
  if (!dateStr) return "No date";

  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch (e) {
    return new Date(dateStr).toLocaleDateString();
  }
}

// Extract the folder name from the path
function getFolderName(path: string): string {
  console.info("Extracting folder name from path:", path);
  const parts = path.split("/");
  return parts[parts.length - 1] || path;
}

// Function to initiate archive download
function downloadArchive(archivePath: string | null): void {
  if (!archivePath) {
    console.error("Archive path is not available");
    return;
  }

  const downloadUrl = directoryStore.getDownloadUrl(archivePath);
  window.open(downloadUrl, "_blank");
}

// Watch for active mission changes and fetch data if needed
watch(
  () => activeMission.value,
  (newMission) => {
    if (
      newMission &&
      (!directoryData.value.length ||
        directoryData.value[0]?.folder_key?.split("/")[0] !== newMission)
    ) {
      directoryStore.fetchAllDirectoryData();
    }
  },
  { immediate: true },
);
</script>

<style scoped>
.directory-tree-container {
  width: 100%;
}

.list-files {
  max-height: 400px;
  overflow-y: auto;
}

.has-files {
  background-color: rgba(0, 0, 0, 0.03);
}
</style>
