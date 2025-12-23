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
  last_checked_time?: string | null;
  last_processed_time?: string | null;
  error_message?: string | null;
}

const emit = defineEmits<{
  missionSelect: [missionKey: string];
  missionHover: [missionKey: string | null];
}>();

const props = defineProps<{
  missions: Mission[];
  selectedMission?: string | null;
  hoveredMission?: string | null;
  zoomToMission?: string | null;
  hiddenMissions?: Set<string>;
}>();

// Constants
const DEFAULT_CENTER: [number, number] = [6.566, 46.52];
const DEFAULT_ZOOM = 8;
const NEUTRAL_COLOR = "#9e9e9e";
const NEUTRAL_LINE_COLOR = "#616161";

const OPACITY = {
  HOVERED: 0.5,
  SELECTED: 0.6,
  NORMAL: 0.3,
} as const;

const directoryStore = useDirectoryStore();
const mapContainer = ref<HTMLDivElement>();
const isLoading = ref(true);

let map: maplibregl.Map | null = null;
let popup: maplibregl.Popup | null = null;
const missionFootprints = ref<Record<string, any>>({});
const missionColors = ref<Record<string, string>>({});
const hoveredLineId = ref<string | null>(null);
const allFeatures = ref<any[]>([]);

function generateColorFromKey(key: string): string {
  let hash = 0;
  for (let i = 0; i < key.length; i++) {
    hash = key.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = Math.abs(hash % 360);
  return `hsl(${hue}, 70%, 50%)`;
}

function varyColorForLine(baseColor: string, lineIndex: number): string {
  // Extract hue from base color HSL format
  const hueMatch = baseColor.match(/hsl\((\d+),/);
  if (!hueMatch) return baseColor;

  const baseHue = parseInt(hueMatch[1]);
  // Vary hue by small increments based on sequential line index
  const hueShift = ((lineIndex * 8) % 40) - 20;
  const newHue = (baseHue + hueShift + 360) % 360;

  // Also vary lightness slightly for better distinction
  const lightness = 50 + ((lineIndex % 5) * 3 - 6);

  return `hsl(${newHue}, 70%, ${lightness}%)`;
}

function createPaintExpression(fallback: string) {
  return [
    "case",
    // Highlight the specific hovered line
    ["==", ["get", "feature_id"], hoveredLineId.value || ""],
    ["get", "color"],
    // Highlight selected mission lines
    ["==", ["get", "mission_key"], props.selectedMission || ""],
    ["get", "color"],
    // If there's a hovered line or selected mission, dim others
    [
      "any",
      ["!=", hoveredLineId.value || "", ""],
      ["!=", props.selectedMission || "", ""],
    ],
    fallback,
    // Otherwise show the mission's color
    ["get", "color"],
  ] as any;
}

function createOpacityExpression() {
  return [
    "case",
    // Full opacity for hovered line
    ["==", ["get", "feature_id"], hoveredLineId.value || ""],
    0.8,
    // Selected mission lines
    ["==", ["get", "mission_key"], props.selectedMission || ""],
    0.7,
    // If there's a hovered line or selected mission, dim others
    [
      "any",
      ["!=", hoveredLineId.value || "", ""],
      ["!=", props.selectedMission || "", ""],
    ],
    0.2,
    // Otherwise normal opacity
    OPACITY.NORMAL,
  ] as any;
}

function extendBoundsFromGeometry(
  bounds: maplibregl.LngLatBounds,
  geometry: any,
) {
  if (geometry.type === "Polygon") {
    geometry.coordinates[0].forEach((coord: number[]) => {
      if (coord.length >= 2) bounds.extend([coord[0], coord[1]]);
    });
  } else if (geometry.type === "MultiPolygon") {
    geometry.coordinates.forEach((polygon: number[][][]) => {
      polygon[0].forEach((coord: number[]) => {
        if (coord.length >= 2) bounds.extend([coord[0], coord[1]]);
      });
    });
  }
}

// Initialize the map
onMounted(async () => {
  if (!mapContainer.value) return;

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
          paint: {
            "raster-saturation": -0.75,
            "raster-brightness-min": 0.5,
          },
        },
      ],
    },
    center: DEFAULT_CENTER,
    zoom: DEFAULT_ZOOM,
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

    map.addLayer({
      id: "mission-footprints-fill",
      type: "fill",
      source: "mission-footprints",
      paint: {
        "fill-color": createPaintExpression(NEUTRAL_COLOR),
        "fill-opacity": createOpacityExpression(),
      },
    });

    map.addLayer({
      id: "mission-footprints-line",
      type: "line",
      source: "mission-footprints",
      paint: {
        "line-color": createPaintExpression(NEUTRAL_LINE_COLOR),
        "line-width": 1,
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

    // Add click handler for map background to deselect
    map.on("click", (e) => {
      if (!map) return;
      const features = map.queryRenderedFeatures(e.point, {
        layers: ["mission-footprints-fill"],
      });
      // If no features clicked, deselect
      if (!features.length) {
        emit("missionSelect", "");
      }
    });

    map.on("mouseenter", "mission-footprints-fill", handleMouseEnter);
    map.on("mousemove", "mission-footprints-fill", handleMouseMove);
    map.on("mouseleave", "mission-footprints-fill", handleMouseLeave);

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

watch(
  () => props.hiddenMissions,
  () => {
    updateVisibleFeatures();
  },
  { deep: true },
);

watch([() => props.selectedMission, hoveredLineId], updateMapStyling);

watch(
  () => props.zoomToMission,
  (missionKey) => {
    if (missionKey) zoomToMission(missionKey);
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
          mission.processing_status !== "error" &&
          !props.hiddenMissions?.has(mission.mission_key),
      )
      .map(async (mission) => {
        try {
          const geojson = await directoryStore.fetchPointcloudGeojson(
            mission.mission_key,
          );

          if (!missionColors.value[mission.mission_key]) {
            missionColors.value[mission.mission_key] = generateColorFromKey(
              mission.mission_key,
            );
          }

          if (geojson?.features) {
            geojson.features.forEach((feature: any, index: number) => {
              if (
                feature.geometry?.type === "Polygon" ||
                feature.geometry?.type === "MultiPolygon"
              ) {
                const lineId = feature.properties?.raster_val || index + 1;
                const lineColor = varyColorForLine(
                  missionColors.value[mission.mission_key],
                  index,
                );
                const featureId = `${mission.mission_key}_${lineId}`;

                feature.properties = {
                  ...feature.properties,
                  mission_key: mission.mission_key,
                  processing_status: mission.processing_status,
                  last_checked_time: mission.last_checked_time,
                  last_processed_time: mission.last_processed_time,
                  error_message: mission.error_message,
                  color: lineColor,
                  line_id: lineId,
                  feature_id: featureId,
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

    allFeatures.value = features;
    updateVisibleFeatures();

    if (features.length > 0) {
      const bounds = new maplibregl.LngLatBounds();
      features.forEach((feature) =>
        extendBoundsFromGeometry(bounds, feature.geometry),
      );

      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, {
          padding: 50,
        });
      }
    }
  } catch (error) {
    console.error("Error loading mission footprints:", error);
  } finally {
    isLoading.value = false;
  }
}

function updateVisibleFeatures() {
  if (!map) return;

  const visibleFeatures = allFeatures.value.filter(
    (feature) => !props.hiddenMissions?.has(feature.properties.mission_key),
  );

  const source = map.getSource(
    "mission-footprints",
  ) as maplibregl.GeoJSONSource;
  source?.setData({
    type: "FeatureCollection",
    features: visibleFeatures,
  });
}

function zoomToMission(missionKey: string) {
  const geojson = missionFootprints.value[missionKey];
  if (!map || !geojson?.features?.length) return;

  const bounds = new maplibregl.LngLatBounds();
  geojson.features.forEach((feature: any) =>
    extendBoundsFromGeometry(bounds, feature.geometry),
  );

  if (!bounds.isEmpty()) {
    map.fitBounds(bounds, {
      padding: 100,
      duration: 1000,
    });
  }
}

function updateMapStyling() {
  if (!map) return;

  map.setPaintProperty(
    "mission-footprints-fill",
    "fill-color",
    createPaintExpression(NEUTRAL_COLOR),
  );
  map.setPaintProperty(
    "mission-footprints-line",
    "line-color",
    createPaintExpression(NEUTRAL_LINE_COLOR),
  );
  map.setPaintProperty(
    "mission-footprints-fill",
    "fill-opacity",
    createOpacityExpression(),
  );
}

function handleMouseEnter(e: maplibregl.MapLayerMouseEvent) {
  if (!map) return;

  map.getCanvas().style.cursor = "pointer";
  const feature = e.features?.[0];
  const missionKey = feature?.properties?.mission_key;
  console.log("Hovering over mission:", missionKey);
  if (missionKey) {
    emit("missionHover", missionKey);

    const {
      processing_status,
      last_checked_time,
      last_processed_time,
      line_id,
    } = feature.properties;
    const status = processing_status || "unknown";

    const popupContent = `
      <div class="mission-popup">
        <h4>${missionKey}</h4>
        ${line_id ? `<p><strong>Line ID:</strong> ${line_id}</p>` : ""}
        <p><strong>Status:</strong> ${status.charAt(0).toUpperCase() + status.slice(1)}</p>
        ${last_checked_time ? `<p><strong>Last Checked:</strong> ${new Date(last_checked_time).toLocaleString()}</p>` : ""}
        ${last_processed_time ? `<p><strong>Last Processed:</strong> ${new Date(last_processed_time).toLocaleString()}</p>` : ""}
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

function handleMouseMove(e: maplibregl.MapLayerMouseEvent) {
  if (!map || !popup || !e.lngLat) return;

  const feature = e.features?.[0];
  if (!feature) return;

  const missionKey = feature.properties?.mission_key;
  const featureId = feature.properties?.feature_id;
  const { processing_status, last_checked_time, last_processed_time, line_id } =
    feature.properties;
  const status = processing_status || "unknown";
  // Update hovered line ID for highlighting
  hoveredLineId.value = featureId;
  // Update hovered line ID
  hoveredLineId.value = featureId;

  // Update popup position and content
  const popupContent = `
    <div class="mission-popup">
      <h4>${missionKey}</h4>
      ${line_id ? `<p><strong>Line ID:</strong> ${line_id}</p>` : ""}
      <p><strong>Status:</strong> ${status.charAt(0).toUpperCase() + status.slice(1)}</p>
      ${last_checked_time ? `<p><strong>Last Checked:</strong> ${new Date(last_checked_time).toLocaleString()}</p>` : ""}
      ${last_processed_time ? `<p><strong>Last Processed:</strong> ${new Date(last_processed_time).toLocaleString()}</p>` : ""}
      <p class="popup-hint">Click to select mission</p>
    </div>
  `;

  popup.setLngLat(e.lngLat).setHTML(popupContent);

  // Emit hover event if mission changed
  if (missionKey) {
    emit("missionHover", missionKey);
  }
}

function handleMouseLeave() {
  if (!map) return;

  map.getCanvas().style.cursor = "";
  hoveredLineId.value = null;
  emit("missionHover", null);
  popup?.remove();
  popup = null;
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
