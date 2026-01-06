<template>
  <q-expansion-item
    label="Classification"
    icon="category"
    header-class="text-subtitle2"
  >
    <div class="q-pt-sm q-pb-md">
      <div class="filter-actions q-px-md q-pb-sm">
        <q-btn
          flat
          dense
          size="sm"
          label="Color by classification"
          :color="isColoredByClassification ? 'grey-5' : 'primary'"
          @click="colorByClassification"
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

      <div v-if="!availableClasses.length" class="empty-state">
        <q-spinner color="primary" size="24px" />
      </div>

      <div v-else class="classification-list">
        <div
          v-for="classValue in availableClasses"
          :key="classValue"
          class="classification-item"
        >
          <q-checkbox
            v-model="selectedClasses[classValue]"
            dense
            color="primary"
            @update:model-value="updateSelectedClasses"
          />
          <div
            class="classification-indicator"
            :style="{ backgroundColor: getClassColor(classValue) }"
            @click.stop
          >
            <q-popup-proxy
              cover
              transition-show="scale"
              transition-hide="scale"
            >
              <q-color
                :model-value="getClassColor(classValue)"
                @update:model-value="(val) => updateClassColor(classValue, val)"
              />
            </q-popup-proxy>
            <q-tooltip>Click to change color</q-tooltip>
          </div>
          <label
            class="classification-content"
            @click="toggleClass(classValue)"
          >
            <div class="classification-label">
              {{ getClassLabel(classValue) }}
            </div>
            <div v-if="classCount(classValue)" class="classification-count">
              {{ formatCount(classCount(classValue)) }} points
            </div>
          </label>
        </div>
      </div>
    </div>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { usePointcloudStore } from "@/stores/pointcloudStore";
import { getClassificationInfo } from "@/types/classification";

const pointcloudStore = usePointcloudStore();
const selectedClasses = ref<Record<number, boolean>>({});

// Use available classifications from store
const availableClasses = computed(
  () => pointcloudStore.availableClassifications,
);

// Check if already colored by classification
const isColoredByClassification = computed(
  () => pointcloudStore.activeAttribute.toLowerCase() === "classification",
);

// Watch for available classifications changes
watch(
  availableClasses,
  (classes) => {
    if (classes.length > 0) {
      // Initialize all as selected
      const selection: Record<number, boolean> = {};
      classes.forEach((classValue) => {
        selection[classValue] = true;
      });
      selectedClasses.value = selection;
      updateSelectedClasses();
    }
  },
  { immediate: true },
);

function capitalizeFirstLetter(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function getClassLabel(value: number): string {
  const potreeClass = pointcloudStore.potreeClassifications[value];
  if (potreeClass) {
    return `${capitalizeFirstLetter(potreeClass.name)}`;
  }
  const info = getClassificationInfo(value);
  return info ? `${info.label}` : `Class ${value}`;
}

function getClassColor(value: number): string {
  const potreeClass = pointcloudStore.potreeClassifications[value];
  if (potreeClass?.color) {
    // Convert Potree color [r, g, b, a] (0-1) to hex
    const r = Math.round(potreeClass.color[0] * 255);
    const g = Math.round(potreeClass.color[1] * 255);
    const b = Math.round(potreeClass.color[2] * 255);
    return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
  }
  const info = getClassificationInfo(value);
  return info?.color ?? "#808080";
}

function updateClassColor(classValue: number, newColor: string | null) {
  if (!newColor) return;

  const potreeClass = pointcloudStore.potreeClassifications[classValue];
  if (potreeClass) {
    // Convert hex to Potree color format [r, g, b, a] (0-1)
    const hex = newColor.replace("#", "");
    const r = parseInt(hex.substring(0, 2), 16) / 255;
    const g = parseInt(hex.substring(2, 4), 16) / 255;
    const b = parseInt(hex.substring(4, 6), 16) / 255;
    potreeClass.color = [r, g, b, 1];
  }
}

function classCount(value: number): number {
  const histogram = pointcloudStore.classificationAttribute?.histogram;
  return histogram?.[value] ?? 0;
}

function formatCount(count: number): string {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(2)}M`;
  } else if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  }
  return count.toString();
}

function updateSelectedClasses() {
  const selectedArray = Object.entries(selectedClasses.value)
    .filter(([_, isSelected]) => isSelected)
    .map(([classValue]) => parseInt(classValue));

  pointcloudStore.setSelectedClassifications(selectedArray);
}

function selectAll() {
  const selection: Record<number, boolean> = { ...selectedClasses.value };
  pointcloudStore.availableClassifications.forEach((classValue) => {
    selection[classValue] = true;
  });
  selectedClasses.value = selection;
  updateSelectedClasses();
}

function selectNone() {
  const selection: Record<number, boolean> = { ...selectedClasses.value };
  pointcloudStore.availableClassifications.forEach((classValue) => {
    selection[classValue] = false;
  });
  selectedClasses.value = selection;
  updateSelectedClasses();
}

function colorByClassification() {
  pointcloudStore.setActiveAttribute("classification");
}

function toggleClass(classValue: number) {
  selectedClasses.value[classValue] = !selectedClasses.value[classValue];
  updateSelectedClasses();
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

.classification-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0;
  padding: 0 16px 8px;
}

.classification-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  margin: 2px 0;
  min-width: 0;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.classification-item:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.classification-indicator {
  width: 18px;
  height: 18px;
  border-radius: 3px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
  cursor: pointer;
}

.classification-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  cursor: pointer;
}

.classification-label {
  font-size: 13px;
  line-height: 1.3;
}

.classification-count {
  font-size: 12px;
  color: #9e9e9e;
  line-height: 1.2;
}
</style>
