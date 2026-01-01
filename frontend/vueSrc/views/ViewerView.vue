<script setup lang="ts">
import { watch, computed } from "vue";
import { useRouter } from "vue-router";
import { useDirectoryStore } from "@/stores/directoryStore";
import MainAppLayout from "@/layouts/MainAppLayout.vue";
import PointCloudViewer from "@/components/pointcloud/PointCloudViewer.vue";
import ViewerSidebar from "@/components/pointcloud/ViewerSidebar.vue";
import { useAppMeta } from "@/composables/useMeta";

const props = defineProps<{
  missionId: string;
}>();

useAppMeta({ title: props.missionId });

const router = useRouter();
const directoryStore = useDirectoryStore();

const missionName = computed(
  () =>
    directoryStore.missionData?.name ||
    directoryStore.activeMission ||
    props.missionId,
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
  <main-app-layout show-back-button @back="handleBack">
    <template #sidebar>
      <viewer-sidebar />
    </template>
    <template #content>
      <div class="full-width full-height relative-position">
        <point-cloud-viewer />
        <div class="floating-banner">
          <div
            class="banner-pill row items-center q-px-lg q-py-sm bg-white shadow-1"
          >
            <q-icon name="location_on" size="16px" class="q-mr-sm" />
            <span class="text-weight-medium">{{ missionName }}</span>
          </div>
        </div>
      </div>
    </template>
  </main-app-layout>
</template>

<style scoped>
.floating-banner {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  pointer-events: none;
}

.banner-pill {
  opacity: 0.92;
  backdrop-filter: blur(12px);
  border-radius: 24px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}
</style>
