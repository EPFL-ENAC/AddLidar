import { defineStore } from "pinia";
import { ref, markRaw } from "vue";

export const usePointCloudStore = defineStore("pointCloud", () => {
  // State as refs
  const activeAttribute = ref("intensity");
  const pointcloudLoaded = ref(false);
  const errorMessage = ref("");

  const volumeTool = ref<
    { startInsertion?: (params: any) => void } | undefined
  >(undefined);

  // Single filter range for current attribute
  const filterMin = ref(0);
  const filterMax = ref(100);

  // Source ID filtering
  const selectedSourceIDs = ref<number[]>([]);
  const availableSourceIDs = ref<number[]>([]);

  const clipPosition = ref({ x: 0, y: 0, z: 0 });
  const clipRotation = ref({ x: 0, y: 0, z: 0 });
  const clipScale = ref({ x: 1, y: 1, z: 1 });

  const clipVolume = ref<any>(null);

  function setClipVolume(volume: any) {
    clipVolume.value = volume;
  }

  function setVolumeTool(tool: any) {
    console.log("setVolumeTool", tool);
    volumeTool.value = markRaw(tool);
  }

  // Source ID filtering methods
  function setSelectedSourceIDs(ids: number[]) {
    selectedSourceIDs.value = ids;
  }

  function setAvailableSourceIDs(ids: number[]) {
    availableSourceIDs.value = ids;
  }

  function clearSourceIDFilter() {
    selectedSourceIDs.value = [];
  }

  // Methods to update clip properties (maintains reactivity)
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
  // Actions as functions
  function setActiveAttribute(attributeName: string) {
    activeAttribute.value = attributeName;

    resetFilterRange();
  }

  function setFilterRange(min: number, max: number) {
    filterMin.value = min;
    filterMax.value = max;
  }

  function resetFilterRange() {
    // Set default ranges based on current attribute
    switch (activeAttribute.value) {
      case "elevation":
        filterMin.value = 0;
        filterMax.value = 1000;
        break;
      case "intensity":
        filterMin.value = 0;
        filterMax.value = 255;
        break;
      default:
        filterMin.value = 0;
        filterMax.value = 100;
    }
  }

  function setErrorMessage(message: string) {
    errorMessage.value = message;
  }

  // Return everything that should be exposed
  return {
    // State
    activeAttribute,
    pointcloudLoaded,
    errorMessage,
    filterMin,
    filterMax,

    clipRotation,
    clipPosition,
    clipScale,
    clipVolume,

    volumeTool,

    selectedSourceIDs,
    availableSourceIDs,

    // Actions
    setClipVolume,
    resetClipVolume,
    setVolumeTool,
    setClipPosition,
    setClipRotation,
    setClipScale,
    setActiveAttribute,
    setErrorMessage,
    setFilterRange,
    // resetFilterRange,

    // Source ID filtering
    setSelectedSourceIDs,
    setAvailableSourceIDs,
    clearSourceIDFilter,
  };
});
