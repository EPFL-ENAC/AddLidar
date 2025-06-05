<template>
  <div class="q-pa-md">
    <q-badge color="primary">
      {{ label }}: {{ range.min }} to {{ range.max }}
    </q-badge>

    <q-range
      v-model="range"
      :min="min"
      :max="max"
      :step="step"
      color="primary"
      label
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { usePointCloudStore } from "@/stores/pointcloud";

const { label, min, max, step } = defineProps({
  label: {
    type: String,
    default: "Filter",
  },
  min: {
    type: Number,
    default: 0,
  },
  max: {
    type: Number,
    default: 100,
  },
  step: {
    type: Number,
    default: 1,
  },
});

const store = usePointCloudStore();

// Create a computed property that gets/sets values in the store
const range = computed({
  get: () => {
    return {
      min: store.filterMin,
      max: store.filterMax,
    };
  },
  set: (value) => {
    store.setFilterRange(value.min, value.max);
  },
});
</script>
