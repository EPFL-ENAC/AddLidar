<script setup lang="ts">
import { watch, computed } from "vue";
import { useRouter } from "vue-router";
import { useDirectoryStore } from "@/stores/directoryStore";
import MainAppLayout from "@/layouts/MainAppLayout.vue";
import PointCloudViewer from "@/components/pointcloud/PointCloudViewer.vue";
import ViewerSidebar from "@/components/pointcloud/ViewerSidebar.vue";

const props = defineProps<{
  missionId: string;
}>();

const router = useRouter();
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

function handleBack() {
  router.push("/");
}
</script>

<template>
  <main-app-layout show-back-button :subtitle="missionName" @back="handleBack">
    <template #sidebar>
      <viewer-sidebar />
    </template>
    <template #content>
      <point-cloud-viewer />
    </template>
  </main-app-layout>
</template>
