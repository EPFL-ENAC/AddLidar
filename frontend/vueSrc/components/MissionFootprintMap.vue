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
import {
  MAX_ZOOM,
  computeMarkerMaxZoom,
  extendBoundsFromGeometry,
  generateColorFromKey,
  varyColorForLine,
} from "@/utils/missionMapHelpers";

interface Mission {
  mission_key: string;
  processing_status: string;
  last_checked_time?: string | null;
  last_processed_time?: string | null;
  error_message?: string | null;
}

interface MissionData {
  key: string;
  color: string;
  centroid: [number, number];
  markerMaxZoom: number;
  polygons: any[];
}

const emit = defineEmits<{
  missionSelect: [missionKey: string];
  missionHover: [missionKey: string | null];
  visibleMissionsChange: [missionKeys: string[]];
}>();

const props = defineProps<{
  missions: Mission[];
  selectedMission?: string | null;
  hoveredMission?: string | null;
  zoomToMission?: string | null;
  hiddenMissions?: Set<string>;
}>();

const DEFAULT_CENTER: [number, number] = [6.566, 46.52];
const DEFAULT_ZOOM = 8;
const NEUTRAL_COLOR = "#9e9e9e";
const NEUTRAL_LINE_COLOR = "#616161";
const MARKER_RADIUS = 11;
const MARKER_RADIUS_HIGHLIGHT = 14;
const CLUSTER_RADIUS_PX = 20;

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
const missionData = new Map<string, MissionData>();
const hoveredLineId = ref<string | null>(null);
const clusterByMission = new Map<string, number>();
let highlightedClusterId: number | null = null;

// === Paint expressions (no zoom — MapLibre forbids ["zoom"] inside case) ===

function createPaintExpression(fallback: string) {
  return [
    "case",
    ["==", ["get", "feature_id"], hoveredLineId.value || ""],
    ["get", "color"],
    [
      "all",
      ["==", ["get", "mission_key"], props.hoveredMission || ""],
      ["!=", props.hoveredMission || "", ""],
    ],
    ["get", "color"],
    ["==", ["get", "mission_key"], props.selectedMission || ""],
    ["get", "color"],
    [
      "any",
      ["!=", hoveredLineId.value || "", ""],
      ["!=", props.selectedMission || "", ""],
      ["!=", props.hoveredMission || "", ""],
    ],
    fallback,
    ["get", "color"],
  ] as any;
}

function createOpacityExpression() {
  return [
    "case",
    ["==", ["get", "feature_id"], hoveredLineId.value || ""],
    0.9,
    [
      "all",
      ["==", ["get", "mission_key"], props.hoveredMission || ""],
      ["!=", props.hoveredMission || "", ""],
      ["==", hoveredLineId.value || "", ""],
    ],
    0.8,
    [
      "all",
      ["==", ["get", "mission_key"], props.selectedMission || ""],
      ["!=", hoveredLineId.value || "", ""],
    ],
    0.5,
    ["==", ["get", "mission_key"], props.selectedMission || ""],
    OPACITY.SELECTED,
    [
      "any",
      ["!=", hoveredLineId.value || "", ""],
      ["!=", props.selectedMission || "", ""],
      ["!=", props.hoveredMission || "", ""],
    ],
    0.15,
    OPACITY.NORMAL,
  ] as any;
}

function createMarkerRadiusExpression() {
  return [
    "case",
    [
      "any",
      ["==", ["get", "mission_key"], props.selectedMission || ""],
      [
        "all",
        ["==", ["get", "mission_key"], props.hoveredMission || ""],
        ["!=", props.hoveredMission || "", ""],
      ],
    ],
    MARKER_RADIUS_HIGHLIGHT,
    MARKER_RADIUS,
  ] as any;
}

// === Map lifecycle ===

onMounted(() => {
  if (!mapContainer.value) return;

  map = new maplibregl.Map({
    container: mapContainer.value,
    style: {
      version: 8,
      glyphs: "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf",
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

  map.on("load", () => {
    if (!map) return;
    addLayers(map);
    bindMapEvents(map);
    loadMissionFootprints();
  });
});

onUnmounted(() => {
  if (map) {
    map.remove();
    map = null;
  }
});

function addLayers(m: maplibregl.Map) {
  m.addSource("mission-footprints", {
    type: "geojson",
    data: { type: "FeatureCollection", features: [] },
  });

  m.addLayer({
    id: "mission-footprints-fill",
    type: "fill",
    source: "mission-footprints",
    paint: {
      "fill-color": createPaintExpression(NEUTRAL_COLOR),
      "fill-opacity": createOpacityExpression(),
    },
  });

  m.addLayer({
    id: "mission-footprints-line",
    type: "line",
    source: "mission-footprints",
    paint: {
      "line-color": createPaintExpression(NEUTRAL_LINE_COLOR),
      "line-width": 1,
    },
  });

  m.addLayer({
    id: "mission-footprints-selected-outline",
    type: "line",
    source: "mission-footprints",
    paint: {
      "line-color": "#1976d2",
      "line-width": [
        "case",
        ["==", ["get", "mission_key"], props.selectedMission || ""],
        3,
        0,
      ],
      "line-opacity": 1,
    },
  });

  m.addSource("mission-centroids", {
    type: "geojson",
    data: { type: "FeatureCollection", features: [] },
    cluster: true,
    clusterRadius: CLUSTER_RADIUS_PX,
    clusterMaxZoom: MAX_ZOOM,
  });

  m.addLayer({
    id: "mission-clusters",
    type: "circle",
    source: "mission-centroids",
    filter: ["has", "point_count"],
    paint: {
      "circle-color": [
        "case",
        ["boolean", ["feature-state", "hovered"], false],
        "#42a5f5",
        "#1976d2",
      ],
      "circle-radius": [
        "case",
        ["boolean", ["feature-state", "hovered"], false],
        ["+", ["step", ["get", "point_count"], 14, 10, 18, 50, 24], 4],
        ["step", ["get", "point_count"], 14, 10, 18, 50, 24],
      ],
      "circle-stroke-color": "#ffffff",
      "circle-stroke-width": [
        "case",
        ["boolean", ["feature-state", "hovered"], false],
        3,
        2,
      ],
      "circle-opacity": 0.85,
    },
  });

  m.addLayer({
    id: "mission-cluster-count",
    type: "symbol",
    source: "mission-centroids",
    filter: ["has", "point_count"],
    layout: {
      "text-field": ["get", "point_count_abbreviated"],
      "text-font": ["Open Sans Semibold"],
      "text-size": 12,
      "text-allow-overlap": true,
    },
    paint: { "text-color": "#ffffff" },
  });

  m.addLayer({
    id: "mission-unclustered-points",
    type: "circle",
    source: "mission-centroids",
    filter: ["!", ["has", "point_count"]],
    paint: {
      "circle-color": ["get", "color"],
      "circle-radius": createMarkerRadiusExpression(),
      "circle-stroke-color": "#ffffff",
      "circle-stroke-width": 2,
      "circle-opacity": 0.95,
    },
  });
}

function bindMapEvents(m: maplibregl.Map) {
  m.on("click", "mission-footprints-fill", (e) => {
    const key = e.features?.[0]?.properties?.mission_key;
    if (key) emit("missionSelect", key);
  });

  m.on("click", "mission-unclustered-points", (e) => {
    const key = e.features?.[0]?.properties?.mission_key;
    if (key) emit("missionSelect", key);
  });

  m.on("click", "mission-clusters", (e) => {
    const feature = e.features?.[0];
    const clusterId = feature?.properties?.cluster_id;
    if (clusterId == null) return;
    const source = m.getSource("mission-centroids") as maplibregl.GeoJSONSource;
    source.getClusterExpansionZoom(clusterId).then((zoom) => {
      const geom = feature.geometry as { coordinates: [number, number] };
      m.easeTo({ center: geom.coordinates, zoom });
    });
  });

  m.on("click", (e) => {
    const features = m.queryRenderedFeatures(e.point, {
      layers: [
        "mission-footprints-fill",
        "mission-unclustered-points",
        "mission-clusters",
      ],
    });
    if (!features.length) emit("missionSelect", "");
  });

  m.on("mouseenter", "mission-footprints-fill", handlePolygonHover);
  m.on("mousemove", "mission-footprints-fill", handlePolygonHover);
  m.on("mouseleave", "mission-footprints-fill", clearHover);

  m.on("mouseenter", "mission-unclustered-points", handleMarkerHover);
  m.on("mouseleave", "mission-unclustered-points", clearHover);
  m.on("mouseenter", "mission-clusters", () => {
    m.getCanvas().style.cursor = "pointer";
  });
  m.on("mouseleave", "mission-clusters", () => {
    m.getCanvas().style.cursor = "";
  });

  m.on("moveend", emitVisibleMissions);
  m.on("zoomend", () => {
    rebuildSources();
    emitVisibleMissions();
  });
}

// === Watchers ===

watch(() => props.missions, loadMissionFootprints, { deep: true });
watch(() => props.hiddenMissions, rebuildSources, { deep: true });
watch(
  [() => props.selectedMission, () => props.hoveredMission, hoveredLineId],
  updateMapStyling,
);
watch(
  () => props.hoveredMission,
  (key) => highlightClusterForMission(key ?? null),
);
watch(
  () => props.zoomToMission,
  (key) => {
    if (key) zoomToMission(key);
  },
);

// === Data loading ===

async function loadMissionFootprints() {
  if (!map || !props.missions.length) return;
  isLoading.value = true;

  try {
    await Promise.all(
      props.missions
        .filter(
          (m) =>
            m.processing_status !== "pending" &&
            m.processing_status !== "error",
        )
        .map(loadOneMission),
    );

    rebuildSources();

    const allBounds = new maplibregl.LngLatBounds();
    missionData.forEach((data) =>
      data.polygons.forEach((f) =>
        extendBoundsFromGeometry(allBounds, f.geometry),
      ),
    );
    if (!allBounds.isEmpty()) map.fitBounds(allBounds, { padding: 50 });

    emitVisibleMissions();
  } catch (err) {
    console.error("Error loading mission footprints:", err);
  } finally {
    isLoading.value = false;
  }
}

async function loadOneMission(mission: Mission) {
  if (missionData.has(mission.mission_key)) return; // already loaded

  try {
    const geojson = await directoryStore.fetchPointcloudGeojson(
      mission.mission_key,
    );
    if (!geojson?.features) return;

    const baseColor = generateColorFromKey(mission.mission_key);
    const bounds = new maplibregl.LngLatBounds();
    const polygons: any[] = [];

    geojson.features.forEach((feature: any, index: number) => {
      if (
        feature.geometry?.type !== "Polygon" &&
        feature.geometry?.type !== "MultiPolygon"
      )
        return;

      const lineId = feature.properties?.raster_val || index + 1;
      feature.properties = {
        ...feature.properties,
        mission_key: mission.mission_key,
        processing_status: mission.processing_status,
        last_checked_time: mission.last_checked_time,
        last_processed_time: mission.last_processed_time,
        error_message: mission.error_message,
        color: varyColorForLine(baseColor, index),
        line_id: lineId,
        feature_id: `${mission.mission_key}_${lineId}`,
      };
      polygons.push(feature);
      extendBoundsFromGeometry(bounds, feature.geometry);
    });

    if (polygons.length === 0 || bounds.isEmpty()) return;

    const center = bounds.getCenter();
    missionData.set(mission.mission_key, {
      key: mission.mission_key,
      color: baseColor,
      centroid: [center.lng, center.lat],
      markerMaxZoom: computeMarkerMaxZoom(bounds),
      polygons,
    });
  } catch (err) {
    console.warn(
      `Failed to load footprint for mission ${mission.mission_key}:`,
      err,
    );
  }
}

// === Single source-of-truth for what's rendered ===

function rebuildSources() {
  if (!map) return;
  const z = map.getZoom();
  const hidden = props.hiddenMissions ?? new Set<string>();

  const polygonFeatures: any[] = [];
  const markerFeatures: any[] = [];

  missionData.forEach((data) => {
    if (hidden.has(data.key)) return;
    if (z >= data.markerMaxZoom) {
      polygonFeatures.push(...data.polygons);
    } else {
      markerFeatures.push({
        type: "Feature",
        geometry: { type: "Point", coordinates: data.centroid },
        properties: { mission_key: data.key, color: data.color },
      });
    }
  });

  (
    map.getSource("mission-footprints") as maplibregl.GeoJSONSource | undefined
  )?.setData({ type: "FeatureCollection", features: polygonFeatures });
  (
    map.getSource("mission-centroids") as maplibregl.GeoJSONSource | undefined
  )?.setData({ type: "FeatureCollection", features: markerFeatures });
  scheduleClusterIndexRebuild();
}

// === Cluster hover sync ===

function highlightClusterForMission(missionKey: string | null) {
  if (!map) return;
  if (highlightedClusterId != null) {
    map.removeFeatureState({
      source: "mission-centroids",
      id: highlightedClusterId,
    });
    highlightedClusterId = null;
  }
  if (!missionKey) return;
  const clusterId = clusterByMission.get(missionKey);
  if (clusterId == null) return;
  map.setFeatureState(
    { source: "mission-centroids", id: clusterId },
    { hovered: true },
  );
  highlightedClusterId = clusterId;
}

async function rebuildClusterIndex() {
  if (!map) return;
  clusterByMission.clear();
  const source = map.getSource("mission-centroids") as
    | maplibregl.GeoJSONSource
    | undefined;
  if (!source) return;
  const clusterFeatures = map.queryRenderedFeatures(undefined, {
    layers: ["mission-clusters"],
  });
  await Promise.all(
    clusterFeatures.map(async (f) => {
      const cid = f.properties?.cluster_id as number | undefined;
      if (cid == null) return;
      const leaves = await source.getClusterLeaves(cid, Infinity, 0);
      leaves.forEach((leaf) => {
        const mk = leaf.properties?.mission_key as string | undefined;
        if (mk) clusterByMission.set(mk, cid);
      });
    }),
  );
  highlightClusterForMission(props.hoveredMission ?? null);
}

function scheduleClusterIndexRebuild() {
  if (!map) return;
  // `idle` fires once all sources are loaded AND the current frame has rendered,
  // which is required for queryRenderedFeatures to see the new clusters.
  map.once("idle", () => {
    rebuildClusterIndex();
  });
}

function emitVisibleMissions() {
  if (!map) return;
  const bounds = map.getBounds();
  const visible: string[] = [];
  missionData.forEach((data) => {
    if (props.hiddenMissions?.has(data.key)) return;
    if (bounds.contains(data.centroid)) visible.push(data.key);
  });
  emit("visibleMissionsChange", visible);
}

function zoomToMission(key: string) {
  const data = missionData.get(key);
  if (!map || !data) return;
  const bounds = new maplibregl.LngLatBounds();
  data.polygons.forEach((f) => extendBoundsFromGeometry(bounds, f.geometry));
  if (!bounds.isEmpty()) {
    map.fitBounds(bounds, { padding: 100, duration: 1000 });
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
    "mission-footprints-fill",
    "fill-opacity",
    createOpacityExpression(),
  );
  map.setPaintProperty(
    "mission-footprints-line",
    "line-color",
    createPaintExpression(NEUTRAL_LINE_COLOR),
  );
  map.setPaintProperty("mission-footprints-selected-outline", "line-width", [
    "case",
    ["==", ["get", "mission_key"], props.selectedMission || ""],
    3,
    0,
  ] as any);
  if (map.getLayer("mission-unclustered-points")) {
    map.setPaintProperty(
      "mission-unclustered-points",
      "circle-radius",
      createMarkerRadiusExpression(),
    );
  }
}

// === Hover / popup ===

function buildPopupHtml(opts: {
  missionKey: string;
  status: string;
  lineId?: number | string | null;
  lastChecked?: string | null;
  lastProcessed?: string | null;
}) {
  const statusLabel =
    opts.status.charAt(0).toUpperCase() + opts.status.slice(1);
  return `
    <div class="mission-popup">
      <h4>${opts.missionKey}</h4>
      ${opts.lineId ? `<p><strong>Line ID:</strong> ${opts.lineId}</p>` : ""}
      <p><strong>Status:</strong> ${statusLabel}</p>
      ${opts.lastChecked ? `<p><strong>Last Checked:</strong> ${new Date(opts.lastChecked).toLocaleString()}</p>` : ""}
      ${opts.lastProcessed ? `<p><strong>Last Processed:</strong> ${new Date(opts.lastProcessed).toLocaleString()}</p>` : ""}
      <p class="popup-hint">Click to select mission</p>
    </div>
  `;
}

function showPopup(lngLat: maplibregl.LngLatLike, html: string) {
  if (!map) return;
  if (!popup) {
    popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });
  }
  popup.setLngLat(lngLat).setHTML(html).addTo(map);
}

function handlePolygonHover(e: maplibregl.MapLayerMouseEvent) {
  if (!map) return;
  const feature = e.features?.[0];
  if (!feature) return;

  map.getCanvas().style.cursor = "pointer";
  const props_ = feature.properties as any;
  hoveredLineId.value = props_.feature_id;
  emit("missionHover", props_.mission_key);
  showPopup(
    e.lngLat,
    buildPopupHtml({
      missionKey: props_.mission_key,
      status: props_.processing_status || "unknown",
      lineId: props_.line_id,
      lastChecked: props_.last_checked_time,
      lastProcessed: props_.last_processed_time,
    }),
  );
}

function handleMarkerHover(e: maplibregl.MapLayerMouseEvent) {
  if (!map) return;
  const key = e.features?.[0]?.properties?.mission_key;
  if (!key) return;

  map.getCanvas().style.cursor = "pointer";
  emit("missionHover", key);

  const mission = props.missions.find((m) => m.mission_key === key);
  showPopup(
    e.lngLat,
    buildPopupHtml({
      missionKey: key,
      status: mission?.processing_status || "unknown",
      lastChecked: mission?.last_checked_time,
      lastProcessed: mission?.last_processed_time,
    }),
  );
}

function clearHover() {
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
