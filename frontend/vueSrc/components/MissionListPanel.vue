<template>
  <aside class="mission-list-panel">
    <header class="q-pa-md">
      <div class="row items-center justify-between q-mb-xs">
        <h1 class="text-h6 q-ma-none">Missions</h1>
        <q-badge color="primary" :label="visibleMissions.length" />
      </div>
      <p class="text-caption text-grey-6 q-ma-none">
        Select a mission to explore LiDAR data
      </p>
    </header>

    <q-separator />

    <q-table
      flat
      :rows="visibleMissions"
      :columns="columns"
      row-key="mission_key"
      :pagination="pagination"
      class="mission-table"
      :selected="selectedRows"
    >
      <!-- Custom body to control row classes -->
      <template #body="props">
        <q-tr
          :props="props"
          class="cursor-pointer"
          @click="handleRowClick($event, props.row)"
        >
          <q-td v-for="col in props.cols" :key="col.name" :props="props">
            <template v-if="col.name === 'name'">
              <div class="column">
                <div class="text-weight-medium">
                  {{ props.row.name || props.row.mission_key }}
                </div>
                <div v-if="props.row.name" class="text-caption text-grey-6">
                  {{ props.row.mission_key }}
                </div>
              </div>
            </template>
            <template v-else-if="col.name === 'date'">
              {{ formatDate(props.row.date) }}
            </template>
            <template v-else-if="col.name === 'size'">
              <span v-if="props.row.metadata?.points">
                {{ formatNumber(props.row.metadata.points) }} pts
              </span>
              <span v-else class="text-grey-5">N/A</span>
            </template>
            <template v-else-if="col.name === 'hide'">
              <q-checkbox
                :model-value="hiddenMissions.has(props.row.mission_key)"
                @update:model-value="toggleHidden(props.row.mission_key)"
                dense
                @click.stop
              />
            </template>
            <template v-else-if="col.name === 'actions'">
              <q-btn
                flat
                dense
                color="primary"
                label="Explore"
                size="sm"
                @click.stop="handleExplore(props.row.mission_key)"
              />
            </template>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import type { QTableColumn } from "quasar";

interface MissionMetadata {
  points?: number;
  boundingBox?: {
    min: [number, number];
    max: [number, number];
  };
}

interface Mission {
  mission_key: string;
  name?: string | null;
  date?: string | null;
  processing_status: string;
  last_checked_time?: string | null;
  last_processed_time?: string | null;
  error_message?: string | null;
  metadata?: MissionMetadata | null;
}

const emit = defineEmits<{
  select: [missionKey: string];
  hover: [missionKey: string | null];
  explore: [missionKey: string];
}>();

const props = defineProps<{
  missions: Mission[];
  selectedMission?: string | null;
  hoveredMission?: string | null;
}>();

const hiddenMissions = ref(new Set<string>());
const pagination = ref({
  rowsPerPage: 0, // Show all rows
});

const columns: QTableColumn[] = [
  {
    name: "name",
    label: "Name",
    field: "mission_key",
    align: "left",
    sortable: true,
  },
  {
    name: "date",
    label: "Date",
    field: "date",
    align: "left",
    sortable: true,
  },
  {
    name: "size",
    label: "Size",
    field: (row: Mission) => row.metadata?.points || 0,
    align: "left",
    sortable: true,
  },
  {
    name: "hide",
    label: "Hide",
    field: "hide",
    align: "center",
    sortable: false,
  },
  {
    name: "actions",
    label: "Actions",
    field: "actions",
    align: "center",
    sortable: false,
  },
];

const visibleMissions = computed(() =>
  props.missions.filter((m) => !hiddenMissions.value.has(m.mission_key)),
);

const selectedRows = computed(() => {
  if (!props.selectedMission) return [];
  return props.missions.filter((m) => m.mission_key === props.selectedMission);
});

function toggleHidden(missionKey: string) {
  if (hiddenMissions.value.has(missionKey)) {
    hiddenMissions.value.delete(missionKey);
  } else {
    hiddenMissions.value.add(missionKey);
  }
}

function handleRowClick(_evt: Event, row: Mission) {
  emit("select", row.mission_key);
  emit("hover", row.mission_key);
}

function handleExplore(missionKey: string) {
  emit("explore", missionKey);
}

function getRowClass(row: Mission) {
  console.log("Determining row class for mission", row.mission_key);
  const status = row.processing_status?.toLowerCase();
  console.log(
    `Mission: ${row.mission_key}, Status: "${row.processing_status}" -> "${status}"`,
  );
  switch (status) {
    case "completed":
    case "processed":
    case "success":
      return ""; // No background color for successful missions
    case "pending":
      return "row-warning";
    case "error":
    case "failed":
      return "row-error";
    default:
      return "row-unknown";
  }
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "N/A";
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

function formatNumber(num: number | undefined): string {
  if (!num) return "0";
  if (num >= 1_000_000_000) return (num / 1_000_000_000).toFixed(1) + "B";
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
  if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
  return num.toString();
}
</script>

<style scoped>
.mission-list-panel {
  width: 100%;
  border-left: 1px solid var(--border-color);
  background: white;
  display: flex;
  flex-direction: column;
}

.mission-table {
  flex: 1;
}

:deep(.q-table tbody tr) {
  cursor: pointer;
}

:deep(.q-table__card) {
  box-shadow: none;
}

:deep(.q-table tbody tr.row-warning) {
  background-color: rgba(255, 152, 0, 0.12) !important;
}

:deep(.q-table tbody tr.row-error) {
  background-color: rgba(244, 67, 54, 0.12) !important;
}

:deep(.q-table tbody tr.row-unknown) {
  background-color: rgba(158, 158, 158, 0.1) !important;
}

:deep(.q-table tbody tr.row-warning:hover),
:deep(.q-table tbody tr.row-error:hover),
:deep(.q-table tbody tr.row-unknown:hover) {
  background-color: rgba(var(--q-primary-rgb), 0.15) !important;
}

:deep(.q-table tbody tr:hover) {
  background-color: rgba(var(--q-primary-rgb), 0.05);
}
</style>
