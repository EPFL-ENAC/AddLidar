<template>
  <q-expansion-item icon="palette" label="Appearance">
    <q-card flat>
      <q-card-section>
        <q-option-group
          v-model="selectedAttribute"
          :options="attributeOptions"
          type="radio"
          color="primary"
        />
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { usePointcloudStore } from "@/stores/pointcloudStore";

const pointcloudStore = usePointcloudStore();

// Setup attribute options
const defaultAttributes = [
  { label: "RGBA", value: "rgba" },
  { label: "RGB", value: "rgb" },
  { label: "Line", value: "line" },
  { label: "Classification", value: "classification" },
  { label: "Intensity", value: "intensity" },
  { label: "Elevation", value: "elevation" },
  { label: "Group", value: "Group" },
  { label: "Normal", value: "Normal" },
  { label: "Distance", value: "Distance" },
  { label: "GPS Time", value: "gps-time" },
];

const attributeOptions = computed(() => {
  if (!pointcloudStore.attributes.length) {
    return defaultAttributes;
  }
  return [{ label: "Color (rgba default)", value: "rgba" }].concat(
    pointcloudStore.attributes.map((attr) => ({
      label: attr.name,
      value: attr.name,
    })),
  );
});

// Use a computed property with getter and setter to sync with store
const selectedAttribute = computed({
  get: () => pointcloudStore.activeAttribute,
  set: (value) => {
    pointcloudStore.setActiveAttribute(value);
  },
});
</script>
