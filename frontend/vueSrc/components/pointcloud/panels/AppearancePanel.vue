<script setup lang="ts">
import { computed } from "vue";
import { usePointcloudStore } from "@/stores/pointcloudStore";

const pointcloudStore = usePointcloudStore();

const defaultAttributes = [
  { label: "RGBA", value: "rgba" },
  { label: "RGB", value: "rgb" },
  { label: "Classification", value: "classification" },
  { label: "Intensity", value: "intensity" },
  { label: "Elevation", value: "elevation" },
  { label: "GPS Time", value: "gps-time" },
];

const attributeOptions = computed(() => {
  if (!pointcloudStore.attributes.length) return defaultAttributes;

  return [{ label: "Color (RGBA)", value: "rgba" }].concat(
    pointcloudStore.attributes.map((attr) => ({
      label: attr.name,
      value: attr.name,
    })),
  );
});

const selectedAttribute = computed({
  get: () => pointcloudStore.activeAttribute,
  set: (value) => pointcloudStore.setActiveAttribute(value),
});
</script>

<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-header__title">Color Mode</span>
    </div>

    <q-list>
      <q-item
        v-for="attr in attributeOptions"
        :key="attr.value"
        tag="label"
        dense
        clickable
        v-ripple
      >
        <q-item-section avatar>
          <q-radio
            v-model="selectedAttribute"
            :val="attr.value"
            color="primary"
          />
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ attr.label }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>
