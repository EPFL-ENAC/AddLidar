<template>
  <div>
    <div
      class="potree_container"
      style="position: absolute; width: 100%; height: 100%; left: 0px; top: 0px"
    >
      <div id="potree_render_area" style="width: 100%; height: 100%">
        <!-- Render error message if any -->
        <ErrorMessage :message="errorMessage"> </ErrorMessage>
      </div>
    </div>
    <div id="potree_sidebar_container"></div>
  </div>
</template>

<script setup>
// Import Three.js and Potree
import { usePointCloudStore } from "@/stores/pointcloud";
import { useDirectoryStore } from "@/stores/directoryStore";
import { ref, onMounted, watch, computed } from "vue";
import ErrorMessage from "./ErrorMessage.vue";

// Use directory store to get active mission
const directoryStore = useDirectoryStore();
const pointcloudId = computed(() => directoryStore.activeMission);
const errorMessage = ref("");
const pointcloudLoaded = ref(false);

const pointcloudStore = usePointCloudStore();

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
  () => [pointcloudStore.filterMin, pointcloudStore.filterMax],
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
        const viewer = window.viewer;
        debugger;
        // If all IDs are selected, clear the filter
        if (selectedIDs.length === pointcloudStore.availableSourceIDs.length) {
          window.viewer.clearFilterPointSourceIDSubset();
        } else {
          // Otherwise set the filter to show only selected IDs
          window.viewer.setFilterPointSourceIDSubset(selectedIDs);
        }
      } else {
        // If none are selected, we could either hide all points or show all points
        // Here we choose to hide all by setting an empty array
        window.viewer.setFilterPointSourceIDSubset([]);
      }
    } catch (error) {
      console.error("Error applying point source ID filter:", error);
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
        // console.log("Point cloud material", pointcloudStore.activeAttribute);
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

  viewer.loadGUI(() => {
    viewer.setLanguage("en");
    // Once GUI is loaded, load the point cloud
    loadPointCloud(pointcloudId.value);
  });
});
</script>
