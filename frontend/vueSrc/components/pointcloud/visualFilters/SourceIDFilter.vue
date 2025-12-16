<template>
  <q-expansion-item icon="filter_list" label="Visual Filters">
    <q-card flat>
      <q-card-section>
        <div class="row items-center justify-between q-mb-md">
          <div>Point Source ID</div>
          <div>
            <q-btn flat dense color="primary" label="All" @click="selectAll" />
            <q-btn
              flat
              dense
              color="primary"
              label="None"
              @click="selectNone"
            />
          </div>
        </div>

        <div v-if="!sourceIDs.length" class="text-center q-pa-md">
          <q-spinner color="primary" size="32px" />
          <div class="q-mt-sm text-grey-6">Loading...</div>
        </div>

        <div v-else class="source-id-list">
          <q-checkbox
            v-for="id in sourceIDs"
            :key="id"
            v-model="selectedIDs[id]"
            :label="`${id}`"
            color="primary"
            @update:model-value="updateSelectedIDs"
          />
        </div>
      </q-card-section>

      <!-- Classification Filter -->
      <q-card-section>
        <classification-filter />
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { usePointcloudStore } from "@/stores/pointcloudStore";
import ClassificationFilter from "./pointcloud/ClassificationFilter.vue";

const pointcloudStore = usePointcloudStore();
const sourceIDs = ref<number[]>([]); // Available source IDs
const selectedIDs = ref<Record<number, boolean>>({}); // Selection state

// Watch for changes in point source ID attribute from metadata
watch(
  () => pointcloudStore.pointSourceIdAttribute,
  (attribute) => {
    if (attribute) {
      initializeSourceIDs(attribute);
    }
  },
  { immediate: true },
);

// Initialize source IDs from metadata
function initializeSourceIDs(attribute: {
  minValue: number | null;
  maxValue: number | null;
}) {
  if (attribute.minValue === null || attribute.maxValue === null) return;

  const minID = attribute.minValue;
  const maxID = attribute.maxValue;

  console.log(`Point Source ID range: ${minID} to ${maxID}`);

  // Generate source IDs based on the range
  const ids: number[] = [];
  if (maxID - minID < 30) {
    for (let id = minID; id <= maxID; id++) {
      ids.push(id);
    }
  } else {
    for (let id = minID; id <= maxID; id++) {
      if (id === minID || id === maxID || (id - minID) % 5 === 0) {
        ids.push(id);
      }
    }
  }

  sourceIDs.value = ids;
  pointcloudStore.setAvailableSourceIDs(ids);

  // Initialize selection (all selected by default)
  const selection: Record<number, boolean> = {};
  ids.forEach((id: number) => {
    selection[id] = true;
  });
  selectedIDs.value = selection;

  updateSelectedIDs();
}

onMounted(() => {
  if (pointcloudStore.pointSourceIdAttribute) {
    initializeSourceIDs(pointcloudStore.pointSourceIdAttribute);
  }
});

function updateSelectedIDs() {
  const selectedIDsArray = Object.entries(selectedIDs.value)
    .filter(([_, isSelected]) => isSelected)
    .map(([id]) => parseInt(id));

  pointcloudStore.setSelectedSourceIDs(selectedIDsArray);
}

function selectAll() {
  const selection: Record<number, boolean> = { ...selectedIDs.value };
  sourceIDs.value.forEach((id) => {
    selection[id] = true;
  });
  selectedIDs.value = selection;
  updateSelectedIDs();
}

function selectNone() {
  const selection: Record<number, boolean> = { ...selectedIDs.value };
  sourceIDs.value.forEach((id) => {
    selection[id] = false;
  });
  selectedIDs.value = selection;
  updateSelectedIDs();
}
</script>

<style scoped>
.source-id-list {
  max-height: 250px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
}
</style>
