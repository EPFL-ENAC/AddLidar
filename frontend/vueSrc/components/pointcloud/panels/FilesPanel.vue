<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useQuasar } from "quasar";
import type { QTableColumn } from "quasar";
import { useDirectoryStore } from "@/stores/directoryStore";

const directoryStore = useDirectoryStore();
const $q = useQuasar();
const searchTerm = ref("");
const pagination = ref({
  sortBy: "name" as string | null,
  descending: false,
  page: 1,
  rowsPerPage: 0, // Show all rows
});

const directoryData = computed(() => directoryStore.directoryData);
const isLoading = computed(() => directoryStore.isLoading);
const error = computed(() => directoryStore.error);
const activeMission = computed(() => directoryStore.activeMission);

const allColumns: QTableColumn[] = [
  {
    name: "name",
    label: "Name",
    field: "folder_key",
    align: "left",
    sortable: true,
    format: (val: string) => getFolderName(val),
  },
  {
    name: "size",
    label: "Size",
    field: "size_kb",
    align: "left",
    sortable: true,
    format: (val: number) => formatSize(val),
  },
  {
    name: "files",
    label: "Files",
    field: "file_count",
    align: "center",
    sortable: true,
  },
  {
    name: "actions",
    label: "",
    field: "actions",
    align: "center",
    sortable: false,
  },
];

const columns = computed(() => {
  const cols = [
    allColumns[0], // name
    allColumns[1], // size
  ];

  // Only show files column on medium screens and larger
  if ($q.screen.gt.sm) {
    cols.push(allColumns[2]); // files
  }

  cols.push(allColumns[3]); // actions (always show)

  return cols;
});

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

  return files;
});

function formatSize(sizeKb: number): string {
  if (sizeKb < 1024) return `${sizeKb || 0} KB`;
  if (sizeKb < 1024 * 1024) return `${(sizeKb / 1024).toFixed(1)} MB`;
  return `${(sizeKb / (1024 * 1024)).toFixed(1)} GB`;
}

function formatDate(dateStr: number | null): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const day = date.getDate().toString().padStart(2, "0");
  const month = (date.getMonth() + 1).toString().padStart(2, "0");
  const year = date.getFullYear().toString().slice(-2);
  return `${day}/${month}/${year}`;
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
  <div class="column full-height bg-white">
    <!-- Search -->
    <div class="q-pa-sm">
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

    <!-- Table Container -->
    <div class="col q-pa-sm q-pt-none" style="min-height: 0; overflow: auto">
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

      <!-- File Table -->
      <q-table
        v-else
        :rows="filteredFiles"
        :columns="columns"
        :pagination="pagination"
        :grid="$q.screen.xs"
        dense
        row-key="folder_key"
        flat
        :bordered="!$q.screen.xs"
        class="sticky-header-table full-height"
        @update:pagination="pagination = $event"
      >
        <!-- Table mode (desktop) -->
        <template #body="props">
          <q-tr :props="props">
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
              <template v-if="col.name === 'name'">
                <span class="folder-name">{{ col.value }}</span>
              </template>
              <template v-else-if="col.name === 'files'">
                <span v-if="props.row.file_count > 0">{{ col.value }}</span>
                <span v-else class="text-grey-5">Empty</span>
              </template>
              <template v-else-if="col.name === 'actions'">
                <q-btn
                  v-if="props.row.file_count > 0"
                  flat
                  dense
                  round
                  icon="download"
                  color="primary"
                  size="sm"
                  @click="downloadArchive(props.row.output_path)"
                >
                  <q-tooltip>Download archive</q-tooltip>
                </q-btn>
              </template>
              <template v-else>
                {{ col.value }}
              </template>
            </q-td>
          </q-tr>
        </template>

        <!-- Grid mode (mobile) -->
        <template #item="props">
          <div class="col-12 q-pa-xs">
            <q-card flat bordered>
              <q-card-section>
                <div class="row items-center q-gutter-sm q-mb-sm">
                  <q-icon
                    :name="props.row.file_count ? 'folder_zip' : 'folder'"
                    color="grey-6"
                  />
                  <div class="text-weight-medium folder-name">
                    {{ getFolderName(props.row.folder_key) }}
                  </div>
                </div>

                <div class="text-caption text-grey-6 q-mb-xs">
                  {{ formatSize(props.row.size_kb) }} ·
                  {{ formatDate(props.row.last_processed) }}
                </div>

                <div class="row items-center justify-between">
                  <div class="text-caption">
                    <span v-if="props.row.file_count > 0">
                      {{ props.row.file_count }}
                      {{ props.row.file_count === 1 ? "file" : "files" }}
                    </span>
                    <span v-else class="text-grey-5">Empty</span>
                  </div>

                  <q-btn
                    v-if="props.row.file_count > 0"
                    flat
                    dense
                    icon="download"
                    color="primary"
                    size="sm"
                    @click="downloadArchive(props.row.output_path)"
                  >
                    <q-tooltip>Download archive</q-tooltip>
                  </q-btn>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </template>

        <!-- No data -->
        <template #no-data>
          <div class="empty-state full-width">
            <div class="empty-state__description">No files found</div>
          </div>
        </template>
      </q-table>
    </div>
  </div>
</template>

<style scoped>
/* Make table scrollable with sticky header */
.sticky-header-table :deep(.q-table__middle) {
  max-height: 100%;
  overflow-y: auto;
  overflow-x: auto;
}

.sticky-header-table :deep(thead tr th) {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: white;
  padding: 8px 12px;
  font-size: 0.75rem;
}

.sticky-header-table :deep(tbody tr) {
  cursor: default;
}

.sticky-header-table :deep(tbody tr:hover) {
  background-color: rgba(var(--q-primary-rgb), 0.04);
}

.sticky-header-table :deep(tbody td) {
  padding: 6px 12px;
  font-size: 0.875rem;
}

.folder-name {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

/* Grid container scrolling */
.sticky-header-table :deep(.q-table__grid-content) {
  max-height: 100%;
  overflow-y: auto;
}
</style>
