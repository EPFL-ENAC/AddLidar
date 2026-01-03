<script setup lang="ts">
import { computed } from "vue";
import { useDirectoryStore } from "@/stores/directoryStore";
import { getClassificationInfo } from "@/types/classification";

const directoryStore = useDirectoryStore();

const missionData = computed(() => directoryStore.missionData);
const metadata = computed(() => directoryStore.pointcloudMetadata);

const extraAttributes = computed(() => {
  if (!missionData.value?.extra_attributes) return null;
  try {
    return JSON.parse(missionData.value.extra_attributes);
  } catch {
    return null;
  }
});

const boundingBoxDimensions = computed(() => {
  const bbox = metadata.value?.boundingBox;
  if (!bbox) return null;

  const [minX, minY, minZ] = bbox.min;
  const [maxX, maxY, maxZ] = bbox.max;

  return {
    width: (maxX - minX).toFixed(2),
    length: (maxY - minY).toFixed(2),
    height: (maxZ - minZ).toFixed(2),
  };
});

const availableClassifications = computed(() => {
  if (!metadata.value?.attributes) return [];

  const classAttr = metadata.value.attributes.find((attr) =>
    attr.name.toLowerCase().includes("classification"),
  );

  if (!classAttr?.histogram) return [];

  return Object.entries(classAttr.histogram)
    .filter(([, count]) => count > 0)
    .map(([value, count]) => ({
      value: parseInt(value),
      count,
      info: getClassificationInfo(parseInt(value)),
    }));
});
</script>

<template>
  <div>
    <q-expansion-item
      label="Mission Details"
      icon="info"
      header-class="text-grey-8"
      default-opened
    >
      <div class="q-pa-md q-pt-sm">
        <div class="q-gutter-y-sm">
          <div v-if="missionData?.name">
            <div class="text-caption text-grey-6 text-uppercase q-mb-xs">
              Name
            </div>
            <div>{{ missionData.name }}</div>
          </div>

          <div v-if="missionData?.date">
            <div class="text-caption text-grey-6 text-uppercase q-mb-xs">
              Date
            </div>
            <div>{{ missionData.date }}</div>
          </div>

          <div>
            <div class="text-caption text-grey-6 text-uppercase q-mb-xs">
              Mission Key
            </div>
            <div class="monospace">{{ missionData?.mission_key }}</div>
          </div>

          <div v-for="(value, key) in extraAttributes" :key="key">
            <div class="text-caption text-grey-6 text-uppercase q-mb-xs">
              {{ key }}
            </div>
            <div>{{ value }}</div>
          </div>
        </div>
      </div>
    </q-expansion-item>

    <q-expansion-item
      label="Point Cloud Statistics"
      icon="scatter_plot"
      header-class="text-grey-8"
    >
      <div class="q-pa-md q-pt-sm">
        <div class="q-gutter-y-sm">
          <div v-if="metadata?.points">
            <div class="text-caption text-grey-6 text-uppercase q-mb-xs">
              Total Points
            </div>
            <div>{{ metadata.points.toLocaleString() }}</div>
          </div>

          <div v-if="metadata?.spacing">
            <div class="text-caption text-grey-6 text-uppercase q-mb-xs">
              Point Spacing
            </div>
            <div>{{ metadata.spacing.toFixed(4) }} m</div>
          </div>

          <div v-if="boundingBoxDimensions">
            <div class="text-caption text-grey-6 text-uppercase q-mb-xs">
              Bounding Box
            </div>
            <div>
              {{ boundingBoxDimensions.width }} ×
              {{ boundingBoxDimensions.length }} ×
              {{ boundingBoxDimensions.height }} m
            </div>
          </div>

          <div v-if="metadata?.projection">
            <div class="text-caption text-grey-6 text-uppercase q-mb-xs">
              Projection
            </div>
            <div class="monospace">{{ metadata.projection }}</div>
          </div>
        </div>
      </div>
    </q-expansion-item>

    <q-expansion-item
      label="Point Attributes"
      icon="data_array"
      header-class="text-grey-8"
    >
      <div class="q-pa-md q-pt-sm">
        <div v-if="!metadata?.attributes?.length" class="empty">
          <q-icon name="info" size="24px" color="grey-5" />
          <p class="q-ma-none">No attributes available</p>
        </div>

        <div v-else class="q-gutter-y-sm">
          <div v-for="attr in metadata.attributes" :key="attr.name">
            <div class="text-caption text-grey-6 text-uppercase q-mb-xs">
              {{ attr.name }}
            </div>
            <div>
              {{ attr.type }}, {{ attr.numElements }} elements
              <span v-if="attr.min && attr.max" class="text-grey-6">
                [{{ attr.min[0]?.toFixed(2) }}, {{ attr.max[0]?.toFixed(2) }}]
              </span>
            </div>
          </div>
        </div>
      </div>
    </q-expansion-item>

    <q-expansion-item
      v-if="availableClassifications.length"
      label="Classification Distribution"
      icon="category"
      header-class="text-grey-8"
    >
      <div class="q-pa-md q-pt-sm">
        <div class="q-gutter-y-sm">
          <div
            v-for="cls in availableClassifications"
            :key="cls.value"
            class="row items-start q-gutter-x-sm"
          >
            <div
              class="indicator"
              :style="{ backgroundColor: cls.info?.color || '#808080' }"
            />
            <div>
              <div>{{ cls.info?.label || `Class ${cls.value}` }}</div>
              <div class="text-caption text-grey-6">
                {{ cls.count.toLocaleString() }} points ({{
                  ((cls.count / (metadata?.points || 1)) * 100).toFixed(1)
                }}%)
              </div>
            </div>
          </div>
        </div>
      </div>
    </q-expansion-item>
  </div>
</template>

<style scoped>
.monospace {
  font-family: monospace;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 0;
  color: #9e9e9e;
}

.indicator {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  flex-shrink: 0;
  margin-top: 2px;
}
</style>
