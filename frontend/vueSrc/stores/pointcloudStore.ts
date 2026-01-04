import { defineStore } from "pinia";
import { ref, computed, watch } from "vue";
import type {
  PointcloudMetadata,
  PointcloudAttribute,
  AttributeType,
} from "@/types/pointcloud";
import { useDirectoryStore } from "./directoryStore";

/** Parsed attribute with convenient accessors */
export interface ParsedAttribute {
  name: string;
  description: string;
  type: AttributeType;
  size: number;
  numElements: number;
  elementSize: number;
  min: number[];
  max: number[];
  scale: number[];
  offset: number[];
  histogram: number[] | null;
  /** Single min value for single-element attributes */
  minValue: number | null;
  /** Single max value for single-element attributes */
  maxValue: number | null;
  /** Whether this attribute has a histogram */
  hasHistogram: boolean;
}

/**
 * Store for pointcloud metadata and visual settings.
 * Handles metadata parsing, attribute extraction, and Potree viewer visual filtering.
 */
export const usePointcloudStore = defineStore("pointcloud", () => {
  const directoryStore = useDirectoryStore();

  // ========== Metadata State ==========
  const metadata = ref<PointcloudMetadata | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Parsed attributes with convenient accessors
  const attributes = ref<ParsedAttribute[]>([]);

  // ========== Visual Filtering State ==========
  const activeAttribute = ref("rgba");
  const selectedSourceIDs = ref<number[]>([]);
  const availableSourceIDs = ref<number[]>([]);
  const selectedClassifications = ref<number[]>([]);
  const availableClassifications = ref<number[]>([]);
  const potreeClassifications = ref<
    Record<string, { visible: boolean; name: string; color: number[] }>
  >({});
  const visualFilterMin = ref(0);
  const visualFilterMax = ref(100);

  // Attribute range filters: { attributeName: [min, max] }
  const attributeRanges = ref<Record<string, [number, number]>>({});

  // Potree viewer tool reference
  const volumeTool = ref<
    { startInsertion?: (params: any) => void } | undefined
  >(undefined);

  // ========== Computed Properties ==========

  /** Get attribute by name (case-insensitive partial match) */
  const getAttributeByName = computed(() => {
    return (namePattern: string): ParsedAttribute | undefined => {
      const pattern = namePattern.toLowerCase();
      return attributes.value.find((attr) =>
        attr.name.toLowerCase().includes(pattern),
      );
    };
  });

  /** Classification attribute with histogram */
  const classificationAttribute = computed(() =>
    getAttributeByName.value("classification"),
  );

  /** Point source ID attribute */
  const pointSourceIdAttribute = computed(() =>
    getAttributeByName.value("point source"),
  );

  /** Intensity attribute */
  const intensityAttribute = computed(() =>
    getAttributeByName.value("intensity"),
  );

  /** Total point count */
  const pointCount = computed(() => metadata.value?.points ?? 0);

  /** Bounding box */
  const boundingBox = computed(() => metadata.value?.boundingBox ?? null);

  /** Available attribute names for coloring */
  const attributeNames = computed(() =>
    attributes.value.map((attr) => attr.name),
  );

  // ========== Actions ==========

  /** Parse raw attribute into ParsedAttribute */
  function parseAttribute(attr: PointcloudAttribute): ParsedAttribute {
    return {
      name: attr.name,
      description: attr.description,
      type: attr.type,
      size: attr.size,
      numElements: attr.numElements,
      elementSize: attr.elementSize,
      min: attr.min,
      max: attr.max,
      scale: attr.scale,
      offset: attr.offset,
      histogram: attr.histogram ?? null,
      minValue: attr.numElements === 1 ? attr.min[0] : null,
      maxValue: attr.numElements === 1 ? attr.max[0] : null,
      hasHistogram: !!attr.histogram && attr.histogram.length > 0,
    };
  }

  /** Set metadata and parse attributes */
  function setMetadata(data: PointcloudMetadata | null) {
    metadata.value = data;

    if (data?.attributes) {
      attributes.value = data.attributes.map(parseAttribute);
      initializeSourceIDs();
      initializeClassifications();
      initializeAttributeRanges();
    } else {
      attributes.value = [];
    }
  }

  /** Initialize source IDs from point source attribute */
  function initializeSourceIDs() {
    const attr = pointSourceIdAttribute.value;
    if (!attr?.minValue || !attr?.maxValue) {
      availableSourceIDs.value = [];
      selectedSourceIDs.value = [];
      return;
    }

    const minID = attr.minValue;
    const maxID = attr.maxValue;
    const ids: number[] = [];

    // If range is small (< 30), include all; otherwise sample
    if (maxID - minID < 30) {
      for (let id = minID; id <= maxID; id++) {
        ids.push(id);
      }
    } else {
      for (let id = minID; id <= maxID; id++) {
        if (id === minID || id === maxID || (id - minID) % 5 === 0) {
          ids.push(id);
        }
      }
    }

    availableSourceIDs.value = ids;
    selectedSourceIDs.value = [...ids]; // All selected by default
  }

  /** Initialize classifications from classification attribute histogram */
  function initializeClassifications() {
    const attr = classificationAttribute.value;
    if (!attr) {
      availableClassifications.value = [];
      selectedClassifications.value = [];
      return;
    }

    if (!attr.histogram) {
      // Fallback to min/max range if no histogram
      if (attr.minValue !== null && attr.maxValue !== null) {
        const classes: number[] = [];
        for (let i = attr.minValue; i <= attr.maxValue; i++) {
          classes.push(i);
        }
        availableClassifications.value = classes;
        selectedClassifications.value = [...classes];
      } else {
        availableClassifications.value = [];
        selectedClassifications.value = [];
      }
      return;
    }

    // Extract classes that have points from histogram
    const classes: number[] = [];
    attr.histogram.forEach((count, classValue) => {
      if (count > 0) {
        classes.push(classValue);
      }
    });

    availableClassifications.value = classes.sort((a, b) => a - b);
    selectedClassifications.value = [...classes]; // All selected by default
  }

  /** Set range for a specific attribute */
  function setAttributeRange(attributeName: string, min: number, max: number) {
    attributeRanges.value[attributeName] = [min, max];
  }

  /** Reset range for a specific attribute to its metadata min/max */
  function resetAttributeRange(attributeName: string) {
    const attr = getAttributeByName.value(attributeName);
    if (attr && attr.minValue !== null && attr.maxValue !== null) {
      attributeRanges.value[attributeName] = [attr.minValue, attr.maxValue];
    }
  }

  /** Clear range filter for a specific attribute */
  function clearAttributeRange(attributeName: string) {
    delete attributeRanges.value[attributeName];
  }

  /** Initialize all attribute ranges based on metadata */
  function initializeAttributeRanges() {
    const ranges: Record<string, [number, number]> = {};
    attributes.value.forEach((attr) => {
      if (
        attr.numElements === 1 &&
        attr.minValue !== null &&
        attr.maxValue !== null
      ) {
        ranges[attr.name] = [attr.minValue, attr.maxValue];
      }
    });
    attributeRanges.value = ranges;
  }

  /** Set active attribute for point cloud coloring */
  function setActiveAttribute(attributeName: string) {
    activeAttribute.value = attributeName;
    resetVisualFilterRange();
  }

  function setVolumeTool(tool: any) {
    volumeTool.value = tool;
  }

  function setVisualFilterRange(min: number, max: number) {
    visualFilterMin.value = min;
    visualFilterMax.value = max;
  }

  function resetVisualFilterRange() {
    // Try to get range from metadata attribute
    const attr = getAttributeByName.value(activeAttribute.value);
    if (attr && attr.minValue !== null && attr.maxValue !== null) {
      visualFilterMin.value = attr.minValue;
      visualFilterMax.value = attr.maxValue;
      return;
    }

    // Fallback defaults
    switch (activeAttribute.value) {
      case "elevation":
        visualFilterMin.value = 0;
        visualFilterMax.value = 1000;
        break;
      case "intensity":
        visualFilterMin.value = 0;
        visualFilterMax.value = 255;
        break;
      default:
        visualFilterMin.value = 0;
        visualFilterMax.value = 100;
    }
  }

  function setSelectedSourceIDs(ids: number[]) {
    selectedSourceIDs.value = ids;
  }

  function setAvailableSourceIDs(ids: number[]) {
    availableSourceIDs.value = ids;
  }

  function clearSourceIDFilter() {
    selectedSourceIDs.value = [];
  }

  function selectAllSourceIDs() {
    selectedSourceIDs.value = [...availableSourceIDs.value];
  }

  // Classification filtering methods
  function setSelectedClassifications(classes: number[]) {
    selectedClassifications.value = classes;
  }

  function setAvailableClassifications(classes: number[]) {
    availableClassifications.value = classes;
  }

  function clearClassificationFilter() {
    selectedClassifications.value = [];
  }

  function selectAllClassifications() {
    selectedClassifications.value = [...availableClassifications.value];
  }

  function setPotreeClassifications(
    classifications: Record<
      string,
      { visible: boolean; name: string; color: number[] }
    >,
  ) {
    potreeClassifications.value = classifications;
  }

  // ========== Watch for metadata changes from directoryStore ==========
  watch(
    () => directoryStore.pointcloudMetadata,
    (newMetadata) => {
      setMetadata(newMetadata);
    },
    { immediate: true },
  );

  return {
    // Metadata state
    metadata,
    attributes,
    isLoading,
    error,

    // Computed
    getAttributeByName,
    classificationAttribute,
    pointSourceIdAttribute,
    intensityAttribute,
    pointCount,
    boundingBox,
    attributeNames,

    // Visual filtering state
    activeAttribute,
    selectedSourceIDs,
    availableSourceIDs,
    selectedClassifications,
    availableClassifications,
    potreeClassifications,
    visualFilterMin,
    visualFilterMax,
    attributeRanges,
    volumeTool,

    // Actions
    setMetadata,
    setActiveAttribute,
    setVolumeTool,
    setVisualFilterRange,
    resetVisualFilterRange,
    setSelectedSourceIDs,
    setAvailableSourceIDs,
    clearSourceIDFilter,
    selectAllSourceIDs,
    setSelectedClassifications,
    setAvailableClassifications,
    clearClassificationFilter,
    selectAllClassifications,
    initializeSourceIDs,
    initializeClassifications,
    setPotreeClassifications,
    setAttributeRange,
    resetAttributeRange,
    clearAttributeRange,
    initializeAttributeRanges,
  };
});
