<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useDirectoryStore } from "@/stores/directoryStore";

const directoryStore = useDirectoryStore();
const searchTerm = ref("");

const directoryData = computed(() => directoryStore.directoryData);
const isLoading = computed(() => directoryStore.isLoading);
const error = computed(() => directoryStore.error);
const activeMission = computed(() => directoryStore.activeMission);

const filteredFiles = computed(() => {
  if (!directoryData.value.length) return [];

  let files = directoryData.value;
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    files = files.filter(
      (item) =>
        getFolderName(item.folder_key).toLowerCase().includes(term) ||
        item.folder_key.toLowerCase().includes(term),
    );
  }

  return files.sort((a, b) =>
    getFolderName(a.folder_key).localeCompare(getFolderName(b.folder_key)),
  );
});

function formatSize(sizeKb: number): string {
  if (sizeKb < 1024) return `${sizeKb || 0} KB`;
  if (sizeKb < 1024 * 1024) return `${(sizeKb / 1024).toFixed(1)} MB`;
  return `${(sizeKb / (1024 * 1024)).toFixed(1)} GB`;
}

function formatDate(dateStr: number | null): string {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function getFolderName(path: string): string {
  const parts = path.split("/");
  return parts[parts.length - 1] || path;
}

function downloadArchive(archivePath: string | null): void {
  if (!archivePath) return;
  window.open(directoryStore.getDownloadUrl(archivePath), "_blank");
}

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

<template>
  <div class="form-section">
    <q-input
      v-model="searchTerm"
      dense
      outlined
      placeholder="Search files..."
      clearable
    >
      <template #prepend>
        <q-icon name="search" size="xs" />
      </template>
    </q-input>
  </div>

  <!-- Loading -->
  <div v-if="isLoading" class="empty-state">
    <q-spinner color="primary" size="32px" />
    <div class="empty-state__description q-mt-sm">Loading files...</div>
  </div>

  <!-- Error -->
  <div v-else-if="error" class="empty-state">
    <q-icon name="error_outline" class="empty-state__icon text-negative" />
    <div class="empty-state__description text-negative">{{ error }}</div>
  </div>

  <!-- No Mission -->
  <div v-else-if="!activeMission" class="empty-state">
    <q-icon name="folder_off" class="empty-state__icon" />
    <div class="empty-state__description">No mission selected</div>
  </div>

  <!-- File List -->
  <q-list v-else separator class="file-list">
    <q-item
      v-for="item in filteredFiles"
      :key="item.folder_key"
      clickable
      :disable="!item.file_count"
      @click="item.file_count && downloadArchive(item.output_path)"
    >
      <q-item-section avatar>
        <q-icon
          :name="item.file_count ? 'folder_zip' : 'folder'"
          color="grey-6"
        />
      </q-item-section>

      <q-item-section>
        <q-item-label>{{ getFolderName(item.folder_key) }}</q-item-label>
        <q-item-label caption>
          {{ formatSize(item.size_kb) }}
          <template v-if="formatDate(item.last_processed)">
            · {{ formatDate(item.last_processed) }}
          </template>
        </q-item-label>
      </q-item-section>

      <q-item-section side>
        <q-badge
          v-if="item.file_count"
          color="primary"
          :label="item.file_count"
        />
        <q-badge v-else color="grey-4" text-color="grey-7" label="Empty" />
      </q-item-section>
    </q-item>

    <div v-if="!filteredFiles.length" class="empty-state">
      <div class="empty-state__description">No files found</div>
    </div>
  </q-list>
</template>

<style scoped>
.file-list {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}
</style>
