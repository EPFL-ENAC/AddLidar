<template>
  <q-card flat>
    <q-card-section>
      <div class="text-subtitle2 text-weight-medium q-mb-sm">{{ label }}</div>
      <div class="q-mb-md">
        <q-chip color="primary" text-color="white" size="sm">
          {{ range.min }} to {{ range.max }}
        </q-chip>
      </div>
      <q-range
        v-model="range"
        :min="min"
        :max="max"
        :step="step"
        color="primary"
        label
        label-always
      />
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { usePointcloudStore } from "@/stores/pointcloudStore";

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

const pointcloudStore = usePointcloudStore();

// Create a computed property that gets/sets values in the store
const range = computed({
  get: () => ({
    min: pointcloudStore.visualFilterMin,
    max: pointcloudStore.visualFilterMax,
  }),
  set: (value) => {
    pointcloudStore.setVisualFilterRange(value.min, value.max);
  },
});
</script>
