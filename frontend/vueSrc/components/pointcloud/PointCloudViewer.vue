<template>
  <div
    class="potree_container"
    style="position: relative; width: 100%; height: 100%"
  >
    <div id="potree_render_area" style="width: 100%; height: 100%">
      <!-- Render error message if any -->
      <ErrorMessage :message="errorMessage"> </ErrorMessage>
    </div>
    <div id="potree_sidebar_container"></div>
  </div>
</template>

<script setup>
// Import Three.js and Potree
import { useExportJobStore } from "@/stores/exportJobStore";
import { usePointcloudStore } from "@/stores/pointcloudStore";
import { useDirectoryStore } from "@/stores/directoryStore";
import { ref, onMounted, watch, computed } from "vue";
import ErrorMessage from "@/components/pointcloud/ErrorMessage.vue";

// Use directory store to get active mission
const directoryStore = useDirectoryStore();
const pointcloudId = computed(() => directoryStore.activeMission);
const errorMessage = ref("");
const pointcloudLoaded = ref(false);

const exportJobStore = useExportJobStore();
const pointcloudStore = usePointcloudStore();

const volume = ref(null);

function showError(message) {
  errorMessage.value = message;
  console.error(message);
}

// Function to change the active attribute
function onAttributeChange(attributeName) {
  if (window.viewer && window.viewer.scene.pointclouds.length > 0) {
    const pointcloud = window.viewer.scene.pointclouds[0];
    const material = pointcloud.material;
    material.activeAttributeName = attributeName;
  }
}

watch(
  () => pointcloudStore.activeAttribute,
  (newValue) => {
    console.log("New attribute", newValue);
    onAttributeChange(newValue);
  },
);

watch(
  () => [pointcloudStore.visualFilterMin, pointcloudStore.visualFilterMax],
  ([newMin, newMax]) => {
    console.log("Filtering source ID", newMin, newMax);
    window.viewer.setFilterPointSourceIDRange(newMin, newMax);
  },
);

// Watch for changes in selected source IDs
watch(
  () => pointcloudStore.selectedSourceIDs,
  (selectedIDs) => {
    if (!window.viewer || !window.viewer.scene.pointclouds.length) return;

    console.log("Source ID filter changed:", selectedIDs);

    try {
      if (selectedIDs.length > 0) {
        // If all IDs are selected, clear the filter
        if (selectedIDs.length === pointcloudStore.availableSourceIDs.length) {
          window.viewer.clearFilterPointSourceIDSubset();
        } else {
          // Otherwise set the filter to show only selected IDs
          window.viewer.setFilterPointSourceIDSubset(selectedIDs);
        }
      } else {
        // If none are selected, hide all by setting an empty array
        window.viewer.setFilterPointSourceIDSubset([]);
      }
    } catch (error) {
      console.error("Error applying point source ID filter:", error);
    }
  },
);

// Watch for changes in selected classifications
watch(
  () => pointcloudStore.selectedClassifications,
  (selectedClasses) => {
    if (!window.viewer || !window.viewer.scene.pointclouds.length) return;

    console.log("Classification filter changed:", selectedClasses);

    try {
      // Get all available classifications from the pointcloud store
      const availableClasses = pointcloudStore.availableClassifications;

      // First, ensure all classifications from metadata exist in viewer.classifications
      // Add missing ones with default colors
      for (const classValue of availableClasses) {
        if (!window.viewer.classifications[classValue]) {
          // Create missing classification with a default color
          window.viewer.classifications[classValue] = {
            visible: true,
            name: `Class ${classValue}`,
            color: [0.5, 0.5, 0.5, 1], // Gray default
          };
        }
      }

      // Get all classification keys from viewer (including ones not in our metadata)
      const allViewerClasses = Object.keys(window.viewer.classifications)
        .filter((key) => key !== "DEFAULT")
        .map((key) => parseInt(key));

      // Set visibility for ALL classifications
      for (const classValue of allViewerClasses) {
        const isVisible = selectedClasses.includes(classValue);
        window.viewer.setClassificationVisibility(classValue, isVisible);
      }

      // Sync classifications to store for UI display
      pointcloudStore.setPotreeClassifications(window.viewer.classifications);
    } catch (error) {
      console.error("Error applying classification filter:", error);
    }
  },
);

// Watch for changes in the active mission
watch(
  () => pointcloudId.value,
  (newId) => {
    if (newId && window.viewer) {
      loadPointCloud(newId);
    }
  },
);

function loadPointCloud(id) {
  try {
    const pointCloudUrl = `${directoryStore.staticBasePath}/Potree/${id}/metadata.json`;
    console.log("Loading point cloud from:", pointCloudUrl);

    // Load point cloud
    Potree.loadPointCloud(pointCloudUrl)
      .then((e) => {
        console.log("point cloud loaded", e);
        const pointcloud = e.pointcloud;
        const material = pointcloud.material;
        material.activeAttributeName = pointcloudStore.activeAttribute;
        material.minSize = 1;
        material.pointSizeType = Potree.PointSizeType.ADAPTIVE;

        // Clear existing point clouds if any
        if (window.viewer.scene.pointclouds.length > 0) {
          for (
            let i = window.viewer.scene.pointclouds.length - 1;
            i >= 0;
            i--
          ) {
            window.viewer.scene.removePointCloud(
              window.viewer.scene.pointclouds[i],
            );
          }
        }

        // Add new pointcloud to the viewer scene
        window.viewer.scene.addPointCloud(pointcloud);
        window.viewer.fitToScreen();

        // Mark pointcloud as loaded
        pointcloudLoaded.value = true;
        errorMessage.value = ""; // Clear any previous errors
      })
      .catch((err) => {
        console.error(err);
        showError(`Failed to load point cloud: ${err.message}`);
      });
  } catch (err) {
    showError(`Error setting up point cloud: ${err.message}`);
    console.error(err);
  }
}

onMounted(() => {
  console.log(
    "Point cloud viewer mounted, active mission:",
    pointcloudId.value,
  );
  if (!pointcloudId.value) {
    showError(
      'No mission selected. Please select a mission or provide a valid "id" query parameter.',
    );
    return;
  }

  window.viewer = new Potree.Viewer(
    document.getElementById("potree_render_area"),
  );
  viewer.setEDLEnabled(true);
  viewer.setFOV(40);
  viewer.setPointBudget(50000000);
  viewer.loadSettingsFromURL();
  viewer.setDescription("");
  console.log(viewer);
  pointcloudStore.setVolumeTool(viewer.volumeTool);
  exportJobStore.setVolumeTool(viewer.volumeTool);

  viewer.loadGUI(() => {
    viewer.setLanguage("en");
    // Once GUI is loaded, load the point cloud
    loadPointCloud(pointcloudId.value);
  });
});
</script>
