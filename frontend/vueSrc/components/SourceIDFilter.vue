<template>
  <div>
    <q-expansion-item label="Source ID Filter" header-class="h2">
      <q-card>
        <q-card-section>
          <div class="row items-center q-mb-sm">
            <div class="col">
              <div class="text-subtitle2">Filter by point source ID</div>
            </div>
            <div class="col-auto">
              <q-btn
                dense
                flat
                icon="select_all"
                label="All"
                @click="selectAll"
              />
              <q-btn
                dense
                flat
                icon="deselect"
                label="None"
                @click="selectNone"
              />
            </div>
          </div>

          <div v-if="!sourceIDs.length" class="text-center q-pa-md">
            <q-spinner color="primary" size="24px" />
            <div class="q-mt-sm text-grey">Loading source IDs...</div>
          </div>

          <div v-else class="source-id-list q-mt-md">
            <q-checkbox
              v-for="id in sourceIDs"
              :key="id"
              dense
              v-model="selectedIDs[id]"
              :label="`ID ${id}`"
              @update:model-value="updateSelectedIDs"
            />
          </div>
        </q-card-section>
      </q-card>
    </q-expansion-item>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { usePointCloudStore } from "@/stores/pointcloud";
import { useDirectoryStore } from "@/stores/directoryStore";

const store = usePointCloudStore();
const directoryStore = useDirectoryStore();
const sourceIDs = ref<number[]>([]); // Available source IDs
const selectedIDs = ref<Record<number, boolean>>({}); // Selection state

// Use a computed property to get the point source ID attribute from metadata
const pointSourceIdAttribute = computed(() => {
  if (!directoryStore.pointcloudMetadata?.attributes) return null;

  return directoryStore.pointcloudMetadata.attributes.find(
    (attr: any) =>
      attr.name.toLowerCase().includes("point source") ||
      attr.name.toLowerCase().includes("pointsource")
  );
});

// Watch for changes in metadata to initialize source IDs
watch(
  () => pointSourceIdAttribute.value,
  (attribute) => {
    if (attribute) {
      initializeSourceIDs(attribute);
    }
  },
  { immediate: true }
);

// Initialize source IDs from metadata
function initializeSourceIDs(attribute: any) {
  if (!attribute || !attribute.min || !attribute.max) return;

  const minID = attribute.min[0];
  const maxID = attribute.max[0];

  console.log(`Point Source ID range: ${minID} to ${maxID}`);

  // Generate source IDs based on the range
  const ids = [];
  // If the range is small (less than 30), include all IDs
  // Otherwise, sample some IDs to avoid UI clutter
  if (maxID - minID < 30) {
    for (let id = minID; id <= maxID; id++) {
      ids.push(id);
    }
  } else {
    // Sample some IDs for larger ranges
    for (let id = minID; id <= maxID; id++) {
      if (id === minID || id === maxID || (id - minID) % 5 === 0) {
        ids.push(id);
      }
    }
  }

  sourceIDs.value = ids;
  store.setAvailableSourceIDs(ids);

  // Initialize selection (all selected by default)
  const selection = {};
  ids.forEach((id) => {
    selection[id] = true;
  });
  selectedIDs.value = selection;

  // Initialize by updating the store
  updateSelectedIDs();
}

// Apply the filter when the viewer is loaded
onMounted(() => {
  // Check if we already have the metadata, if so initialize
  if (pointSourceIdAttribute.value) {
    initializeSourceIDs(pointSourceIdAttribute.value);
  }
});

// Update the store when selections change
function updateSelectedIDs() {
  // Get array of selected IDs
  const selectedIDsArray = Object.entries(selectedIDs.value)
    .filter(([_, isSelected]) => isSelected)
    .map(([id]) => parseInt(id));

  // Update store
  store.setSelectedSourceIDs(selectedIDsArray);
}

// Select all source IDs
function selectAll() {
  const selection = { ...selectedIDs.value };
  sourceIDs.value.forEach((id) => {
    selection[id] = true;
  });
  selectedIDs.value = selection;
  updateSelectedIDs();
}

// Deselect all source IDs
function selectNone() {
  const selection = { ...selectedIDs.value };
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
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}
</style>
