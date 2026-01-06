<template>
  <q-expansion-item
    label="Point Source ID"
    icon="layers"
    header-class="text-subtitle2"
  >
    <div class="q-pt-sm q-pb-md">
      <div class="filter-actions q-px-md q-pb-sm">
        <q-btn
          flat
          dense
          size="sm"
          label="Color by source ID"
          :color="isColoredBySourceID ? 'grey-5' : 'primary'"
          @click="colorBySourceID"
        />
        <q-btn
          flat
          dense
          size="sm"
          label="Select all"
          color="grey-7"
          @click="selectAll"
        />
        <q-btn
          flat
          dense
          size="sm"
          label="Clear"
          color="grey-7"
          @click="selectNone"
        />
      </div>

      <div v-if="!sourceIDs.length" class="empty-state">
        <div class="text-caption text-grey-6">No source IDs available</div>
      </div>

      <div v-else class="source-id-grid">
        <q-checkbox
          v-for="id in sourceIDs"
          :key="id"
          v-model="selectedIDs[id]"
          :label="String(id)"
          dense
          color="primary"
          @update:model-value="updateSelectedIDs"
        />
      </div>
    </div>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { usePointcloudStore } from "@/stores/pointcloudStore";

const pointcloudStore = usePointcloudStore();
const sourceIDs = ref<number[]>([]); // Available source IDs
const selectedIDs = ref<Record<number, boolean>>({}); // Selection state

// Check if already colored by point source ID
const isColoredBySourceID = computed(
  () =>
    pointcloudStore.activeAttribute.toLowerCase() === "point source id" ||
    pointcloudStore.activeAttribute.toLowerCase() === "pointsourceid",
);

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

function colorBySourceID() {
  // Try to find the point source ID attribute name from store
  const pointSourceAttr = pointcloudStore.attributes.find(
    (attr) =>
      attr.name.toLowerCase().includes("point source") ||
      attr.name.toLowerCase().includes("pointsource"),
  );
  if (pointSourceAttr) {
    pointcloudStore.setActiveAttribute(pointSourceAttr.name);
  }
}
</script>

<style scoped>
.filter-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.empty-state {
  display: flex;
  justify-content: center;
  padding: 16px;
}

.source-id-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
  gap: 4px;
  padding: 0 16px 8px;
}
</style>
