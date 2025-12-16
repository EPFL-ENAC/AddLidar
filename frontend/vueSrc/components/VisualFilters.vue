<template>
  <q-expansion-item icon="filter_list" label="Visual Filters">
    <q-card flat>
      <!-- Point Source ID Filter -->
      <q-card-section>
        <point-source-i-d-filter />
      </q-card-section>

      <q-separator />

      <!-- Classification Filter -->
      <q-card-section>
        <classification-filter />
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>

<script setup lang="ts">
import PointSourceIDFilter from "./PointSourceIDFilter.vue";
import ClassificationFilter from "./ClassificationFilter.vue";
</script>
