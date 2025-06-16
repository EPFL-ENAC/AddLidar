<template>
  <div class="mission-footprint-map">
    <div ref="mapContainer" class="map-container"></div>
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">Loading mission footprints...</div>
    </div>
    <div class="map-legend">
      <h4>Mission Status</h4>
      <div class="legend-item">
        <div class="legend-color completed"></div>
        <span>Completed/Processed</span>
      </div>
      <div class="legend-item">
        <div class="legend-color pending"></div>
        <span>Pending</span>
      </div>
      <div class="legend-item">
        <div class="legend-color error"></div>
        <span>Error</span>
      </div>
      <div class="legend-item">
        <div class="legend-color unknown"></div>
        <span>Unknown</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { useDirectoryStore } from "@/stores/directoryStore";

interface Mission {
  mission_key: string;
  processing_status: string;
  last_checked_time: string;
  last_processed_time?: string;
  error_message?: string;
}

const emit = defineEmits<{
  missionSelect: [missionKey: string];
  missionHover: [missionKey: string | null];
}>();

const props = defineProps<{
  missions: Mission[];
  selectedMission?: string | null;
  zoomToMission?: string | null;
}>();

const directoryStore = useDirectoryStore();
const mapContainer = ref<HTMLDivElement>();
const isLoading = ref(true);

let map: maplibregl.Map | null = null;
let popup: maplibregl.Popup | null = null;
const missionFootprints = ref<Record<string, any>>({});

// Initialize the map
onMounted(async () => {
  if (!mapContainer.value) return;

  // Create the map
  map = new maplibregl.Map({
    container: mapContainer.value,
    style: {
      version: 8,
      sources: {
        osm: {
          type: "raster",
          tiles: [
            "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
          ],
          tileSize: 256,
        },
      },
      layers: [
        {
          id: "osm",
          type: "raster",
          source: "osm",
        },
      ],
    },
    center: [6.566, 46.52], // Switzerland coordinates as default
    zoom: 8,
  });

  // Wait for map to load
  map.on("load", () => {
    if (!map) return;

    // Add mission footprints source
    map.addSource("mission-footprints", {
      type: "geojson",
      data: {
        type: "FeatureCollection",
        features: [],
      },
    });

    // Add mission footprints layer (fill)
    map.addLayer({
      id: "mission-footprints-fill",
      type: "fill",
      source: "mission-footprints",
      paint: {
        "fill-color": [
          "case",
          ["==", ["get", "processing_status"], "completed"],
          "#4caf50",
          ["==", ["get", "processing_status"], "processed"],
          "#4caf50",
          ["==", ["get", "processing_status"], "pending"],
          "#ff9800",
          ["==", ["get", "processing_status"], "error"],
          "#f44336",
          "#9e9e9e",
        ],
        "fill-opacity": [
          "case",
          ["==", ["get", "mission_key"], props.selectedMission || ""],
          0.8,
          0.4,
        ],
      },
    });

    // Add mission footprints layer (outline)
    map.addLayer({
      id: "mission-footprints-line",
      type: "line",
      source: "mission-footprints",
      paint: {
        "line-color": [
          "case",
          ["==", ["get", "processing_status"], "completed"],
          "#2e7d32",
          ["==", ["get", "processing_status"], "processed"],
          "#2e7d32",
          ["==", ["get", "processing_status"], "pending"],
          "#ef6c00",
          ["==", ["get", "processing_status"], "error"],
          "#c62828",
          "#616161",
        ],
        "line-width": [
          "case",
          ["==", ["get", "mission_key"], props.selectedMission || ""],
          3,
          2,
        ],
      },
    });

    // Add click handler
    map.on("click", "mission-footprints-fill", (e) => {
      if (e.features && e.features[0]) {
        const missionKey = e.features[0].properties?.mission_key;
        if (missionKey) {
          emit("missionSelect", missionKey);
        }
      }
    });

    // Add hover handlers
    map.on("mouseenter", "mission-footprints-fill", (e) => {
      if (map) {
        map.getCanvas().style.cursor = "pointer";
        if (e.features && e.features[0]) {
          const feature = e.features[0];
          const missionKey = feature.properties?.mission_key;
          if (missionKey) {
            emit("missionHover", missionKey);

            // Create popup with mission info
            const status = feature.properties?.processing_status || "unknown";
            const lastChecked = feature.properties?.last_checked_time;
            const lastProcessed = feature.properties?.last_processed_time;

            const popupContent = `
              <div class="mission-popup">
                <h4>${missionKey}</h4>
                <p><strong>Status:</strong> ${status.charAt(0).toUpperCase() + status.slice(1)}</p>
                ${lastChecked ? `<p><strong>Last Checked:</strong> ${new Date(lastChecked).toLocaleString()}</p>` : ""}
                ${lastProcessed ? `<p><strong>Last Processed:</strong> ${new Date(lastProcessed).toLocaleString()}</p>` : ""}
                <p class="popup-hint">Click to select mission</p>
              </div>
            `;

            popup = new maplibregl.Popup({
              closeButton: false,
              closeOnClick: false,
            })
              .setLngLat(e.lngLat)
              .setHTML(popupContent)
              .addTo(map);
          }
        }
      }
    });

    map.on("mouseleave", "mission-footprints-fill", () => {
      if (map) {
        map.getCanvas().style.cursor = "";
        emit("missionHover", null);

        if (popup) {
          popup.remove();
          popup = null;
        }
      }
    });

    // Load footprints for existing missions
    loadMissionFootprints();
  });
});

// Clean up map on unmount
onUnmounted(() => {
  if (map) {
    map.remove();
    map = null;
  }
});

// Watch for mission changes
watch(
  () => props.missions,
  () => {
    loadMissionFootprints();
  },
  { deep: true },
);

// Watch for selected mission changes
watch(
  () => props.selectedMission,
  () => {
    updateSelectedMission();
  },
);

// Watch for zoom to mission requests
watch(
  () => props.zoomToMission,
  (missionKey) => {
    if (missionKey) {
      zoomToMission(missionKey);
    }
  },
);

// Load footprints for all missions
async function loadMissionFootprints() {
  if (!map || !props.missions.length) return;

  isLoading.value = true;
  const features: any[] = [];

  try {
    // Load footprints for processed missions
    const footprintPromises = props.missions
      .filter(
        (mission) =>
          mission.processing_status !== "pending" &&
          mission.processing_status !== "error",
      )
      .map(async (mission) => {
        try {
          const geojson = await directoryStore.fetchPointcloudGeojson(
            mission.mission_key,
          );

          // Validate GeoJSON structure
          if (geojson && geojson.features && Array.isArray(geojson.features)) {
            geojson.features.forEach((feature: any) => {
              // Only add valid features with geometry
              if (
                feature.geometry &&
                (feature.geometry.type === "Polygon" ||
                  feature.geometry.type === "MultiPolygon")
              ) {
                feature.properties = {
                  ...feature.properties,
                  mission_key: mission.mission_key,
                  processing_status: mission.processing_status,
                  last_checked_time: mission.last_checked_time,
                  last_processed_time: mission.last_processed_time,
                  error_message: mission.error_message,
                };
                features.push(feature);
              }
            });
          }

          missionFootprints.value[mission.mission_key] = geojson;
        } catch (error) {
          console.warn(
            `Failed to load footprint for mission ${mission.mission_key}:`,
            error,
          );
        }
      });

    await Promise.all(footprintPromises);

    // Update the map source
    const source = map.getSource(
      "mission-footprints",
    ) as maplibregl.GeoJSONSource;
    if (source) {
      source.setData({
        type: "FeatureCollection",
        features,
      });
    }

    // Fit map to footprints if we have any
    if (features.length > 0) {
      const bounds = new maplibregl.LngLatBounds();
      features.forEach((feature) => {
        if (feature.geometry.type === "Polygon") {
          feature.geometry.coordinates[0].forEach((coord: number[]) => {
            if (coord.length >= 2) {
              bounds.extend([coord[0], coord[1]]);
            }
          });
        } else if (feature.geometry.type === "MultiPolygon") {
          feature.geometry.coordinates.forEach((polygon: number[][][]) => {
            polygon[0].forEach((coord: number[]) => {
              if (coord.length >= 2) {
                bounds.extend([coord[0], coord[1]]);
              }
            });
          });
        }
      });

      // Only fit bounds if bounds are valid
      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, { padding: 50 });
      }
    }
  } catch (error) {
    console.error("Error loading mission footprints:", error);
  } finally {
    isLoading.value = false;
  }
}

// Zoom to a specific mission's footprint
function zoomToMission(missionKey: string) {
  if (!map || !missionFootprints.value[missionKey]) return;

  const geojson = missionFootprints.value[missionKey];
  if (!geojson || !geojson.features || geojson.features.length === 0) return;

  // Calculate bounds for the mission's footprint
  const bounds = new maplibregl.LngLatBounds();
  geojson.features.forEach((feature: any) => {
    if (feature.geometry.type === "Polygon") {
      feature.geometry.coordinates[0].forEach((coord: number[]) => {
        if (coord.length >= 2) {
          bounds.extend([coord[0], coord[1]]);
        }
      });
    } else if (feature.geometry.type === "MultiPolygon") {
      feature.geometry.coordinates.forEach((polygon: number[][][]) => {
        polygon[0].forEach((coord: number[]) => {
          if (coord.length >= 2) {
            bounds.extend([coord[0], coord[1]]);
          }
        });
      });
    }
  });

  // Fit to the mission's bounds with some padding
  if (!bounds.isEmpty()) {
    map.fitBounds(bounds, {
      padding: 100,
      duration: 1000, // Smooth animation duration in milliseconds
    });
  }
}

// Update the selected mission styling
function updateSelectedMission() {
  if (!map) return;

  // Update the fill opacity for selected mission
  map.setPaintProperty("mission-footprints-fill", "fill-opacity", [
    "case",
    ["==", ["get", "mission_key"], props.selectedMission || ""],
    0.8,
    0.4,
  ]);

  // Update the line width for selected mission
  map.setPaintProperty("mission-footprints-line", "line-width", [
    "case",
    ["==", ["get", "mission_key"], props.selectedMission || ""],
    3,
    2,
  ]);
}
</script>

<style scoped>
.mission-footprint-map {
  position: relative;
  height: 100%;
  width: 100%;
}

.map-container {
  height: 100%;
  width: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Popup styles */
:global(.maplibregl-popup-content) {
  padding: 0;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

:global(.mission-popup) {
  padding: 12px;
  font-family: Arial, sans-serif;
  max-width: 250px;
}

:global(.mission-popup h4) {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

:global(.mission-popup p) {
  margin: 4px 0;
  font-size: 12px;
  color: #666;
}

:global(.mission-popup .popup-hint) {
  font-style: italic;
  color: #999;
  margin-top: 8px;
}

/* Legend styles */
.map-legend {
  position: absolute;
  top: 10px;
  right: 10px;
  background: white;
  padding: 10px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  font-size: 12px;
  z-index: 1000;
}

.map-legend h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: bold;
  color: #333;
}

.legend-item {
  display: flex;
  align-items: center;
  margin: 4px 0;
}

.legend-color {
  width: 12px;
  height: 12px;
  margin-right: 6px;
  border-radius: 2px;
  border: 1px solid rgba(0, 0, 0, 0.2);
}

.legend-color.completed {
  background-color: #4caf50;
}

.legend-color.pending {
  background-color: #ff9800;
}

.legend-color.error {
  background-color: #f44336;
}

.legend-color.unknown {
  background-color: #9e9e9e;
}
</style>
