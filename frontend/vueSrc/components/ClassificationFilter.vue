<template>
  <q-card flat class="q-mt-md">
    <q-card-section>
      <div class="row items-center justify-between q-mb-md">
        <div class="text-subtitle2">Classification</div>
        <div>
          <q-btn flat dense color="primary" label="All" @click="selectAll" />
          <q-btn flat dense color="primary" label="None" @click="selectNone" />
        </div>
      </div>

      <div v-if="!availableClasses.length" class="text-center q-pa-md">
        <q-spinner color="primary" size="32px" />
        <div class="q-mt-sm text-grey-6">Loading...</div>
      </div>

      <div v-else class="classification-list">
        <div
          v-for="classValue in availableClasses"
          :key="classValue"
          class="classification-item"
        >
          <q-checkbox
            v-model="selectedClasses[classValue]"
            color="primary"
            @update:model-value="updateSelectedClasses"
          />
          <div
            class="classification-color cursor-pointer"
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
          <div class="text-body2 classification-label">
            {{ getClassLabel(classValue) }}
            <span v-if="classCount(classValue)" class="text-grey-6">
              ({{ formatCount(classCount(classValue)) }})
            </span>
          </div>
          <q-tooltip>
            {{ getClassDescription(classValue) }}
          </q-tooltip>
        </div>
      </div>
    </q-card-section>
  </q-card>
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
  return info ? `${value} - ${info.label}` : `${value}`;
}

function getClassDescription(value: number): string {
  const potreeClass = pointcloudStore.potreeClassifications[value];
  if (potreeClass) {
    return potreeClass.name;
  }
  const info = getClassificationInfo(value);
  return info ? info.description : `Class ${value}`;
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
</script>

<style scoped>
.classification-list {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.classification-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.classification-color {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.2);
}

.classification-label {
  flex: 1;
}
</style>
