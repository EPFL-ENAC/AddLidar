<script setup lang="ts">
import ColorVariableSelector from "../ColorVariableSelector.vue";
import ClassificationFilter from "../visualFilters/ClassificationFilter.vue";
import PointSourceIDFilter from "../visualFilters/PointSourceIDFilter.vue";
import AttributeRangeFilter from "../visualFilters/AttributeRangeFilter.vue";
</script>

<template>
  <div>
    <ColorVariableSelector />
    <ClassificationFilter />
    <PointSourceIDFilter />
    <AttributeRangeFilter attribute-name="return number" />
    <AttributeRangeFilter attribute-name="number of returns" />
    <AttributeRangeFilter attribute-name="gps-time" />
  </div>
</template>
