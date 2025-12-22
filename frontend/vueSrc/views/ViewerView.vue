<script setup lang="ts">
import { watch, computed } from "vue";
import { useDirectoryStore } from "@/stores/directoryStore";
import ViewerLayout from "@/layouts/ViewerLayout.vue";
import PointCloudViewer from "@/components/pointcloud/PointCloudViewer.vue";
import ViewerSidebar from "@/components/pointcloud/ViewerSidebar.vue";

const props = defineProps<{
  missionId: string;
}>();

const directoryStore = useDirectoryStore();

const missionName = computed(
  () => directoryStore.activeMission || props.missionId,
);

watch(
  () => props.missionId,
  (newId) => {
    if (newId) directoryStore.setActiveMission(newId);
  },
  { immediate: true },
);
</script>

<template>
  <viewer-layout :mission-name="missionName">
    <template #viewer>
      <point-cloud-viewer />
    </template>
    <template #sidebar>
      <viewer-sidebar />
    </template>
  </viewer-layout>
</template>
