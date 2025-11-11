<template>
  <div style="position: relative; height: 100%; width: 100%">
    <div ref="mapContainer" style="height: 100%; width: 100%"></div>
    <div
      v-if="isLoading"
      style="
        position: absolute;
        inset: 0;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 1000;
      "
    >
      <q-spinner color="primary" size="40px" />
      <div class="text-grey-6 q-mt-sm">Loading mission footprints...</div>
    </div>
    <q-card
      flat
      bordered
      style="
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 1000;
        min-width: 160px;
      "
      class="q-pa-sm"
    >
      <div class="text-subtitle2 q-mb-xs">Mission Status</div>
      <div class="column q-gutter-xs">
        <div class="row items-center no-wrap">
          <div
            style="
              width: 12px;
              height: 12px;
              background: #4caf50;
              border-radius: 2px;
            "
            class="q-mr-xs"
          ></div>
          <span class="text-caption">Completed/Processed</span>
        </div>
        <div class="row items-center no-wrap">
          <div
            style="
              width: 12px;
              height: 12px;
              background: #ff9800;
              border-radius: 2px;
            "
            class="q-mr-xs"
          ></div>
          <span class="text-caption">Pending</span>
        </div>
        <div class="row items-center no-wrap">
          <div
            style="
              width: 12px;
              height: 12px;
              background: #f44336;
              border-radius: 2px;
            "
            class="q-mr-xs"
          ></div>
          <span class="text-caption">Error</span>
        </div>
        <div class="row items-center no-wrap">
          <div
            style="
              width: 12px;
              height: 12px;
              background: #9e9e9e;
              border-radius: 2px;
            "
            class="q-mr-xs"
          ></div>
          <span class="text-caption">Unknown</span>
        </div>
      </div>
    </q-card>
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
:global(.maplibregl-popup-content) {
  padding: 0;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

:global(.mission-popup) {
  padding: 12px;
  max-width: 250px;
}

:global(.mission-popup h4) {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
}

:global(.mission-popup p) {
  margin: 4px 0;
  font-size: 12px;
}

:global(.mission-popup .popup-hint) {
  font-style: italic;
  color: #999;
  margin-top: 8px;
}
</style>
