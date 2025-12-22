<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { usePointcloudStore } from "@/stores/pointcloudStore";
import { getClassificationInfo } from "@/types/classification";

const pointcloudStore = usePointcloudStore();

// Classification filter state
const selectedClasses = ref<Record<number, boolean>>({});
const availableClasses = computed(
  () => pointcloudStore.availableClassifications,
);

// Source ID filter state
const selectedSourceIDs = ref<Record<number, boolean>>({});
const sourceIDs = ref<number[]>([]);

// Classification helpers
function getClassLabel(value: number): string {
  const potreeClass = pointcloudStore.potreeClassifications[value];
  if (potreeClass) return potreeClass.name;
  const info = getClassificationInfo(value);
  return info?.label ?? `Class ${value}`;
}

function getClassColor(value: number): string {
  const potreeClass = pointcloudStore.potreeClassifications[value];
  if (potreeClass?.color) {
    const [r, g, b] = potreeClass.color.map((c: number) => Math.round(c * 255));
    return `#${[r, g, b].map((c) => c.toString(16).padStart(2, "0")).join("")}`;
  }
  return getClassificationInfo(value)?.color ?? "#808080";
}

function updateClassColor(classValue: number, newColor: string | null) {
  if (!newColor) return;
  const potreeClass = pointcloudStore.potreeClassifications[classValue];
  if (potreeClass) {
    const hex = newColor.replace("#", "");
    potreeClass.color = [
      parseInt(hex.substring(0, 2), 16) / 255,
      parseInt(hex.substring(2, 4), 16) / 255,
      parseInt(hex.substring(4, 6), 16) / 255,
      1,
    ];
  }
}

function classCount(value: number): number {
  return pointcloudStore.classificationAttribute?.histogram?.[value] ?? 0;
}

function formatCount(count: number): string {
  if (count >= 1e6) return `${(count / 1e6).toFixed(1)}M`;
  if (count >= 1e3) return `${(count / 1e3).toFixed(1)}K`;
  return count.toString();
}

// Classification selection
function updateSelectedClasses() {
  const selected = Object.entries(selectedClasses.value)
    .filter(([, v]) => v)
    .map(([k]) => parseInt(k));
  pointcloudStore.setSelectedClassifications(selected);
}

function selectAllClasses() {
  availableClasses.value.forEach((c) => (selectedClasses.value[c] = true));
  updateSelectedClasses();
}

function selectNoClasses() {
  availableClasses.value.forEach((c) => (selectedClasses.value[c] = false));
  updateSelectedClasses();
}

watch(
  availableClasses,
  (classes) => {
    if (classes.length) {
      classes.forEach((c) => (selectedClasses.value[c] = true));
      updateSelectedClasses();
    }
  },
  { immediate: true },
);

// Source ID helpers
function initializeSourceIDs(attr: {
  minValue: number | null;
  maxValue: number | null;
}) {
  if (attr.minValue === null || attr.maxValue === null) return;

  const ids: number[] = [];
  const range = attr.maxValue - attr.minValue;

  if (range < 30) {
    for (let id = attr.minValue; id <= attr.maxValue; id++) ids.push(id);
  } else {
    for (let id = attr.minValue; id <= attr.maxValue; id++) {
      if (
        id === attr.minValue ||
        id === attr.maxValue ||
        (id - attr.minValue) % 5 === 0
      ) {
        ids.push(id);
      }
    }
  }

  sourceIDs.value = ids;
  pointcloudStore.setAvailableSourceIDs(ids);
  ids.forEach((id) => (selectedSourceIDs.value[id] = true));
  updateSelectedSourceIDs();
}

function updateSelectedSourceIDs() {
  const selected = Object.entries(selectedSourceIDs.value)
    .filter(([, v]) => v)
    .map(([k]) => parseInt(k));
  pointcloudStore.setSelectedSourceIDs(selected);
}

function selectAllSourceIDs() {
  sourceIDs.value.forEach((id) => (selectedSourceIDs.value[id] = true));
  updateSelectedSourceIDs();
}

function selectNoSourceIDs() {
  sourceIDs.value.forEach((id) => (selectedSourceIDs.value[id] = false));
  updateSelectedSourceIDs();
}

watch(
  () => pointcloudStore.pointSourceIdAttribute,
  (attr) => attr && initializeSourceIDs(attr),
  { immediate: true },
);

onMounted(() => {
  if (pointcloudStore.pointSourceIdAttribute) {
    initializeSourceIDs(pointcloudStore.pointSourceIdAttribute);
  }
});
</script>

<template>
  <!-- Classification Filter -->
  <div class="form-section">
    <div class="section-header">
      <span class="section-header__title">Classification</span>
      <div class="q-gutter-x-xs">
        <q-btn flat dense size="sm" label="All" @click="selectAllClasses" />
        <q-btn flat dense size="sm" label="None" @click="selectNoClasses" />
      </div>
    </div>

    <div v-if="!availableClasses.length" class="empty-state">
      <q-spinner color="primary" size="24px" />
    </div>

    <div v-else class="filter-list">
      <label
        v-for="classValue in availableClasses"
        :key="classValue"
        class="filter-item"
      >
        <q-checkbox
          v-model="selectedClasses[classValue]"
          dense
          @update:model-value="updateSelectedClasses"
        />
        <div
          class="color-swatch"
          :style="{ backgroundColor: getClassColor(classValue) }"
          @click.stop.prevent
        >
          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
            <q-color
              :model-value="getClassColor(classValue)"
              @update:model-value="(v) => updateClassColor(classValue, v)"
            />
          </q-popup-proxy>
        </div>
        <span class="filter-label">
          {{ getClassLabel(classValue) }}
          <span v-if="classCount(classValue)" class="text-grey-6">
            ({{ formatCount(classCount(classValue)) }})
          </span>
        </span>
      </label>
    </div>
  </div>

  <q-separator />

  <!-- Point Source ID Filter -->
  <div class="form-section">
    <div class="section-header">
      <span class="section-header__title">Point Source ID</span>
      <div class="q-gutter-x-xs">
        <q-btn flat dense size="sm" label="All" @click="selectAllSourceIDs" />
        <q-btn flat dense size="sm" label="None" @click="selectNoSourceIDs" />
      </div>
    </div>

    <div v-if="!sourceIDs.length" class="empty-state">
      <div class="text-caption text-grey-6">No source IDs available</div>
    </div>

    <div v-else class="source-id-grid">
      <q-checkbox
        v-for="id in sourceIDs"
        :key="id"
        v-model="selectedSourceIDs[id]"
        :label="String(id)"
        dense
        @update:model-value="updateSelectedSourceIDs"
      />
    </div>
  </div>
</template>

<style scoped>
.filter-list {
  max-height: 250px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  cursor: pointer;
}

.color-swatch {
  width: 14px;
  height: 14px;
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  cursor: pointer;
}

.filter-label {
  font-size: 13px;
}

.source-id-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
  gap: 4px;
}
</style>
