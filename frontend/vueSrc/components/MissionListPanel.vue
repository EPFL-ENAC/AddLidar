<template>
  <div class="column full-height bg-white">
    <header class="q-pa-md q-py-md">
      <div class="row items-center justify-between">
        <h1 class="text-h6 q-ma-none">Missions</h1>
      </div>
      <p class="text-caption text-grey-6 q-ma-none">
        Select a mission to explore LiDAR data
      </p>
    </header>

    <div class="col q-pa-sm q-pb-md" style="min-height: 0; overflow: auto">
      <q-table
        :rows="visibleMissions"
        :grid="$q.screen.xs"
        :dense="isTableDense"
        :columns="columns"
        row-key="mission_key"
        :pagination="pagination"
        :selected="selectedRows"
        :bordered="!$q.screen.xs"
        flat
        class="sticky-header-table full-height"
      >
        <!-- Grid mode (mobile) -->
        <template #item="props">
          <div class="col-12 q-pa-xs">
            <q-card
              flat
              bordered
              :class="[
                'mission-card cursor-pointer',
                { 'hidden-card': hiddenMissions.has(props.row.mission_key) },
                { 'selected-card': props.row.mission_key === selectedMission },
              ]"
              @click="handleRowClick($event, props.row)"
            >
              <q-card-section>
                <div class="row items-center justify-between q-mb-sm">
                  <div class="col ellipsis text-weight-medium">
                    {{ props.row.name || props.row.mission_key }}
                  </div>
                  <div class="row items-center q-gutter-xs">
                    <span class="text-caption text-grey-6">Hide</span>
                    <q-checkbox
                      :model-value="hiddenMissions.has(props.row.mission_key)"
                      @update:model-value="toggleHidden(props.row.mission_key)"
                      dense
                      @click.stop
                    >
                      <q-tooltip>Hide from map</q-tooltip>
                    </q-checkbox>
                  </div>
                </div>

                <div class="text-caption text-grey-6 q-mb-xs">
                  {{ props.row.mission_key }}
                </div>

                <div class="row items-center q-gutter-md q-mb-sm">
                  <div class="text-caption">
                    <q-icon name="event" size="xs" class="q-mr-xs" />
                    {{ formatDate(props.row.date) }}
                  </div>
                  <div v-if="props.row.metadata?.points" class="text-caption">
                    <q-icon name="grain" size="xs" class="q-mr-xs" />
                    {{ formatNumber(props.row.metadata.points) }} pts
                  </div>
                </div>

                <q-btn
                  v-if="isProcessed(props.row)"
                  flat
                  color="primary"
                  icon="open_in_new"
                  label="Explore"
                  size="sm"
                  class="full-width"
                  @click.stop="handleExplore(props.row.mission_key)"
                />
                <div v-else class="text-caption text-warning">
                  <q-icon name="warning" size="xs" class="q-mr-xs" />
                  {{ getStatusTooltip(props.row) }}
                </div>
              </q-card-section>

              <!-- Expanded details -->
              <q-card-section
                v-if="props.row.mission_key === selectedMission"
                class="q-pt-none"
              >
                <q-separator class="q-mb-md" />
                <mission-expanded-details
                  :mission="props.row"
                  @explore="handleExplore"
                />
              </q-card-section>
            </q-card>
          </div>
        </template>

        <!-- Table mode (desktop) -->
        <template #body="props">
          <q-tr
            :props="props"
            :class="[
              'cursor-pointer',
              { 'hidden-row': hiddenMissions.has(props.row.mission_key) },
            ]"
            @click="handleRowClick($event, props.row)"
          >
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
              <template v-if="col.name === 'name'">
                <div class="column" style="max-width: 150px">
                  <div class="ellipsis">
                    {{ props.row.name || props.row.mission_key }}
                  </div>
                  <div
                    v-if="props.row.name"
                    class="text-caption text-grey-6 ellipsis"
                  >
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
                  v-if="isProcessed(props.row)"
                  flat
                  color="primary"
                  outline
                  push
                  icon="open_in_new"
                  @click.stop="handleExplore(props.row.mission_key)"
                >
                  <q-tooltip>Explore mission</q-tooltip>
                </q-btn>
                <q-icon v-else name="warning" color="warning" size="sm">
                  <q-tooltip>{{ getStatusTooltip(props.row) }}</q-tooltip>
                </q-icon>
              </template>
            </q-td>
          </q-tr>

          <!-- Expanded row content -->
          <q-tr v-if="props.row.mission_key === selectedMission" :props="props">
            <q-td colspan="100%">
              <mission-expanded-details
                :mission="props.row"
                @explore="handleExplore"
              />
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useQuasar } from "quasar";
import type { QTableColumn } from "quasar";
import MissionExpandedDetails from "./MissionExpandedDetails.vue";

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
  detailed_error_message?: string | null;
  extra_attributes?: string | null;
  metadata?: MissionMetadata | null;
}

const emit = defineEmits<{
  select: [missionKey: string | null];
  hover: [missionKey: string | null];
  explore: [missionKey: string];
  hiddenMissionsChange: [hiddenMissions: Set<string>];
}>();

const props = defineProps<{
  missions: Mission[];
  selectedMission?: string | null;
  hoveredMission?: string | null;
}>();

const $q = useQuasar();
const hiddenMissions = ref(new Set<string>());
const pagination = ref({
  rowsPerPage: 0, // Show all rows
});

const allColumns: QTableColumn[] = [
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

const isTableDense = computed(() => {
  const value = $q.screen.xs || $q.screen.sm;
  console.log("isTableDense", value);
  return value;
});
const columns = computed(() => {
  const cols = [
    allColumns[0], // Always show name
  ];

  // Add date if screen is medium or larger
  if ($q.screen.gt.md) {
    cols.push(allColumns[1]); // date
  }

  if ($q.screen.gt.lg) {
    cols.push(allColumns[2]); // size
  }

  // Always show hide and actions
  cols.push(allColumns[3]); // hide
  cols.push(allColumns[4]); // actions

  return cols;
});

const visibleMissions = computed(() => props.missions);

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
  emit("hiddenMissionsChange", new Set(hiddenMissions.value));
}

function handleRowClick(_evt: Event, row: Mission) {
  // Toggle selection: unselect if clicking the same row
  if (props.selectedMission === row.mission_key) {
    emit("select", null);
    emit("hover", null);
  } else {
    emit("select", row.mission_key);
    emit("hover", row.mission_key);
  }
}

function handleExplore(missionKey: string) {
  emit("explore", missionKey);
}

function isProcessed(row: Mission): boolean {
  const status = row.processing_status?.toLowerCase();
  return (
    status === "completed" || status === "processed" || status === "success"
  );
}

function getStatusTooltip(row: Mission): string {
  const status = row.processing_status?.toLowerCase();
  if (status === "pending") return "Processing in progress";
  if (status === "error" || status === "failed") {
    return row.error_message || "Processing failed";
  }
  return "Mission not available";
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
:deep(.q-table tbody tr) {
  cursor: pointer;
}

:deep(.q-table tbody td) {
  padding-top: 1.25rem !important;
  padding-bottom: 1.25rem !important;
}

:deep(.q-table thead th) {
  padding-top: 1rem !important;
  padding-bottom: 1rem !important;
}

:deep(.q-table__card) {
  box-shadow: none;
}

:deep(.q-table tbody tr:hover) {
  background-color: rgba(var(--q-primary-rgb), 0.001) !important;
}

:deep(.q-table tbody tr.hidden-row) {
  opacity: 0.4;
  background-color: rgba(0, 0, 0, 0.02) !important;
}

:deep(.q-table tbody tr.hidden-row:hover) {
  opacity: 0.6;
}

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
}

/* Grid mode styles */
.mission-card {
  transition: all 0.2s;
}

.mission-card:hover {
  background-color: rgba(var(--q-primary-rgb), 0.02);
}

.selected-card {
  border-color: var(--q-primary);
  background-color: rgba(var(--q-primary-rgb), 0.05);
}

.hidden-card {
  opacity: 0.5;
}

/* Grid container scrolling */
.sticky-header-table :deep(.q-table__grid-content) {
  max-height: 100%;
  overflow-y: auto;
}
</style>
