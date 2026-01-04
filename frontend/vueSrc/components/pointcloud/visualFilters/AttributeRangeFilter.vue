<template>
  <q-expansion-item
    v-if="attribute"
    :label="getAttributeLabel(attribute)"
    icon="tune"
    header-class="text-grey-8"
  >
    <div v-if="rangeValue" class="q-pt-xs q-px-md q-pb-md overflow-hidden">
      <div class="row items-center justify-end q-gutter-x-xs q-pb-sm">
        <q-btn
          flat
          dense
          size="sm"
          :label="`Color by ${getAttributeLabel(attribute).toLowerCase()}`"
          :color="isColoredBy ? 'grey-5' : 'primary'"
          @click="colorByAttribute"
        />
        <q-btn
          flat
          dense
          size="sm"
          label="Reset"
          color="grey-7"
          @click="resetRange"
        />
      </div>

      <div class="column q-gutter-y-sm q-mb-lg">
        <q-range
          v-model="rangeValue"
          :min="attribute.minValue!"
          :max="attribute.maxValue!"
          :step="getAttributeStep(attribute)"
          color="primary"
          label-always
          switch-label-side
          @update:model-value="updateRange"
        />
      </div>
    </div>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { usePointcloudStore } from "@/stores/pointcloudStore";
import { getAttributeLabel, getAttributeStep } from "@/types/attributeFilters";

interface Props {
  attributeName: string;
}

const props = defineProps<Props>();
const pointcloudStore = usePointcloudStore();

// Get the specific attribute from store
const attribute = computed(() =>
  pointcloudStore.attributes.find(
    (attr) => attr.name.toLowerCase() === props.attributeName.toLowerCase(),
  ),
);

// Local range value for this attribute (Quasar expects { min, max })
const rangeValue = ref<{ min: number; max: number } | null>(null);

// Initialize range when attribute is available
watch(
  attribute,
  (attr) => {
    if (attr && attr.minValue !== null && attr.maxValue !== null) {
      rangeValue.value = { min: attr.minValue, max: attr.maxValue };
    }
  },
  { immediate: true },
);

const isColoredBy = computed(() => {
  if (!attribute.value) return false;
  return (
    pointcloudStore.activeAttribute.toLowerCase() ===
    attribute.value.name.toLowerCase()
  );
});

function colorByAttribute() {
  if (attribute.value) {
    pointcloudStore.setActiveAttribute(attribute.value.name);
  }
}

function updateRange() {
  if (attribute.value && rangeValue.value) {
    pointcloudStore.setAttributeRange(
      attribute.value.name,
      rangeValue.value.min,
      rangeValue.value.max,
    );
  }
}

function resetRange() {
  if (
    attribute.value &&
    attribute.value.minValue !== null &&
    attribute.value.maxValue !== null
  ) {
    rangeValue.value = {
      min: attribute.value.minValue,
      max: attribute.value.maxValue,
    };
    pointcloudStore.resetAttributeRange(attribute.value.name);
  }
}
</script>

<style scoped></style>
