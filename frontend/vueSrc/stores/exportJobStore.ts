import { defineStore } from "pinia";
import { ref, markRaw } from "vue";

/**
 * Store for export job parameters.
 * Handles clip volume (ROI) and export settings for LidarDataManager API.
 * For pointcloud metadata and visual settings, use pointcloudStore instead.
 */
export const useExportJobStore = defineStore("exportJob", () => {
  // Clip volume for ROI (Region of Interest) in export jobs
  const clipPosition = ref({ x: 0, y: 0, z: 0 });
  const clipRotation = ref({ x: 0, y: 0, z: 0 });
  const clipScale = ref({ x: 1, y: 1, z: 1 });
  const clipVolume = ref<any>(null);

  // Volume tool reference (shared with viewer for creating clip volumes)
  const volumeTool = ref<
    { startInsertion?: (params: any) => void } | undefined
  >(undefined);

  function setClipVolume(volume: any) {
    clipVolume.value = volume;
  }

  function setVolumeTool(tool: any) {
    volumeTool.value = markRaw(tool);
  }

  function setClipPosition(position: { x: number; y: number; z: number }) {
    clipPosition.value.x = position.x;
    clipPosition.value.y = position.y;
    clipPosition.value.z = position.z;
  }

  function setClipRotation(rotation: { x: number; y: number; z: number }) {
    clipRotation.value.x = rotation.x;
    clipRotation.value.y = rotation.y;
    clipRotation.value.z = rotation.z;
  }

  function setClipScale(scale: { x: number; y: number; z: number }) {
    clipScale.value.x = scale.x;
    clipScale.value.y = scale.y;
    clipScale.value.z = scale.z;
  }

  function resetClipVolume() {
    setClipPosition({ x: 0, y: 0, z: 0 });
    setClipRotation({ x: 0, y: 0, z: 0 });
    setClipScale({ x: 1, y: 1, z: 1 });
    clipVolume.value = null;
  }

  return {
    // State
    clipRotation,
    clipPosition,
    clipScale,
    clipVolume,
    volumeTool,

    // Actions
    setClipVolume,
    resetClipVolume,
    setVolumeTool,
    setClipPosition,
    setClipRotation,
    setClipScale,
  };
});
