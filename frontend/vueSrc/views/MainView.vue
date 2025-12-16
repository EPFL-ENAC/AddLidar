<script setup lang="ts">
import DownloadDataForm from "@/components/pointcloud/DownloadDataForm.vue";
import PointCloudViewer from "@/components/pointcloud/PointCloudViewer.vue";
import { useDirectoryStore } from "@/stores/directoryStore";
import { watch } from "vue";

const directoryStore = useDirectoryStore();

const props = defineProps({
  id: String,
});

watch(
  () => props.id,
  (newId) => {
    if (newId) directoryStore.setActiveMission(newId);
  },
  { immediate: true },
);
</script>

<template>
  <div class="container">
    <PointCloudViewer></PointCloudViewer>
    <DownloadDataForm></DownloadDataForm>
  </div>
</template>
