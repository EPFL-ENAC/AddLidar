<template>
  <q-expansion-item
    label="Color Mode"
    icon="palette"
    header-class="text-grey-8"
    :default-opened="true"
  >
    <div class="q-pt-sm">
      <q-list class="attribute-grid">
        <q-item
          v-for="attr in attributeOptions"
          :key="attr.value"
          tag="label"
          dense
          clickable
          @mouseenter="previewAttribute(attr.value)"
          @mouseleave="restoreAttribute"
          @click="confirmSelection(attr.value)"
        >
          <q-item-section side>
            <q-radio
              v-model="selectedAttribute"
              :val="attr.value"
              dense
              color="primary"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ attr.label }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { usePointcloudStore } from "@/stores/pointcloudStore";

const pointcloudStore = usePointcloudStore();

// Preview state for hover
const isPreviewMode = ref(false);
const previousAttribute = ref<string>("");

// Setup attribute options - prioritize most commonly used
const defaultAttributes = [
  { label: "RGBA", value: "rgba" },
  { label: "Classification", value: "classification" },
  { label: "Intensity", value: "intensity" },
  { label: "RGB", value: "rgb" },
  { label: "Line", value: "line" },
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

  // Always prioritize Color, Classification, and Intensity at the top
  const priorityAttributes = [{ label: "Color (rgba)", value: "rgba" }];

  // Find classification and intensity in store attributes
  const classificationAttr = pointcloudStore.attributes.find(
    (attr) => attr.name.toLowerCase() === "classification",
  );
  const intensityAttr = pointcloudStore.attributes.find(
    (attr) => attr.name.toLowerCase() === "intensity",
  );

  // Add classification and intensity if they exist
  if (classificationAttr) {
    priorityAttributes.push({
      label: classificationAttr.name,
      value: classificationAttr.name,
    });
  }
  if (intensityAttr) {
    priorityAttributes.push({
      label: intensityAttr.name,
      value: intensityAttr.name,
    });
  }

  // Add remaining attributes (excluding classification and intensity)
  // Keep original order from store
  const remainingAttributes = pointcloudStore.attributes
    .filter(
      (attr) =>
        attr.name.toLowerCase() !== "classification" &&
        attr.name.toLowerCase() !== "intensity",
    )
    .map((attr) => ({
      label: attr.name,
      value: attr.name,
    }));

  return priorityAttributes.concat(remainingAttributes);
});

// Use a computed property with getter and setter to sync with store
const selectedAttribute = computed({
  get: () => pointcloudStore.activeAttribute,
  set: (value) => {
    pointcloudStore.setActiveAttribute(value);
  },
});

// Preview attribute on hover
function previewAttribute(value: string) {
  if (!isPreviewMode.value) {
    previousAttribute.value = pointcloudStore.activeAttribute;
    isPreviewMode.value = true;
  }
  pointcloudStore.setActiveAttribute(value);
}

// Restore previous attribute on mouse leave
function restoreAttribute() {
  if (isPreviewMode.value) {
    pointcloudStore.setActiveAttribute(previousAttribute.value);
    isPreviewMode.value = false;
  }
}

// Confirm selection on click
function confirmSelection(value: string) {
  isPreviewMode.value = false;
  selectedAttribute.value = value;
}
</script>

<style scoped>
.attribute-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0;
}

.attribute-grid .q-item {
  min-width: 0;
}
</style>
