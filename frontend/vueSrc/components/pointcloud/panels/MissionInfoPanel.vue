<script setup lang="ts">
import { computed } from 'vue'
import { useDirectoryStore } from '@/stores/directoryStore'
import { getClassificationInfo } from '@/types/classification'

const directoryStore = useDirectoryStore()

const missionData = computed(() => directoryStore.missionData)
const metadata = computed(() => directoryStore.pointcloudMetadata)

const extraAttributes = computed(() => {
  if (!missionData.value?.extra_attributes) return null
  try {
    return JSON.parse(missionData.value.extra_attributes)
  } catch {
    return null
  }
})

const boundingBoxDimensions = computed(() => {
  const bbox = metadata.value?.boundingBox
  if (!bbox) return null

  const [minX, minY, minZ] = bbox.min
  const [maxX, maxY, maxZ] = bbox.max

  return {
    width: (maxX - minX).toFixed(2),
    length: (maxY - minY).toFixed(2),
    height: (maxZ - minZ).toFixed(2),
  }
})

const availableClassifications = computed(() => {
  if (!metadata.value?.attributes) return []

  const classAttr = metadata.value.attributes.find((attr) =>
    attr.name.toLowerCase().includes('classification')
  )

  if (!classAttr?.histogram) return []

  return Object.entries(classAttr.histogram)
    .filter(([, count]) => count > 0)
    .map(([value, count]) => ({
      value: parseInt(value),
      count,
      info: getClassificationInfo(parseInt(value)),
    }))
})
</script>

<template>
  <div class="panel">
    <q-expansion-item label="Mission Details" icon="info" default-opened>
      <div class="content">
        <div v-if="missionData?.name" class="item">
          <div class="label">Name</div>
          <div>{{ missionData.name }}</div>
        </div>

        <div v-if="missionData?.date" class="item">
          <div class="label">Date</div>
          <div>{{ missionData.date }}</div>
        </div>

        <div class="item">
          <div class="label">Mission Key</div>
          <div class="monospace">{{ missionData?.mission_key }}</div>
        </div>

        <div v-for="(value, key) in extraAttributes" :key="key" class="item">
          <div class="label">{{ key }}</div>
          <div>{{ value }}</div>
        </div>
      </div>
    </q-expansion-item>

    <q-expansion-item label="Point Cloud Statistics" icon="scatter_plot">
      <div class="content">
        <div v-if="metadata?.points" class="item">
          <div class="label">Total Points</div>
          <div>{{ metadata.points.toLocaleString() }}</div>
        </div>

        <div v-if="metadata?.spacing" class="item">
          <div class="label">Point Spacing</div>
          <div>{{ metadata.spacing.toFixed(4) }} m</div>
        </div>

        <div v-if="boundingBoxDimensions" class="item">
          <div class="label">Bounding Box</div>
          <div>
            {{ boundingBoxDimensions.width }} ×
            {{ boundingBoxDimensions.length }} ×
            {{ boundingBoxDimensions.height }} m
          </div>
        </div>

        <div v-if="metadata?.projection" class="item">
          <div class="label">Projection</div>
          <div class="monospace">{{ metadata.projection }}</div>
        </div>
      </div>
    </q-expansion-item>

    <q-expansion-item label="Point Attributes" icon="data_array">
      <div class="content">
        <div v-if="!metadata?.attributes?.length" class="empty">
          <q-icon name="info" size="24px" color="grey-5" />
          <p>No attributes available</p>
        </div>

        <template v-else>
          <div
            v-for="attr in metadata.attributes"
            :key="attr.name"
            class="item"
          >
            <div class="label">{{ attr.name }}</div>
            <div>
              {{ attr.type }}, {{ attr.numElements }} elements
              <span v-if="attr.min && attr.max" class="muted">
                [{{ attr.min[0]?.toFixed(2) }}, {{ attr.max[0]?.toFixed(2) }}]
              </span>
            </div>
          </div>
        </template>
      </div>
    </q-expansion-item>

    <q-expansion-item
      v-if="availableClassifications.length"
      label="Classification Distribution"
      icon="category"
    >
      <div class="content">
        <div
          v-for="cls in availableClassifications"
          :key="cls.value"
          class="classification"
        >
          <div
            class="indicator"
            :style="{ backgroundColor: cls.info?.color || '#808080' }"
          />
          <div>
            <div>{{ cls.info?.label || `Class ${cls.value}` }}</div>
            <div class="muted">
              {{ cls.count.toLocaleString() }} points ({{
                ((cls.count / (metadata?.points || 1)) * 100).toFixed(1)
              }}%)
            </div>
          </div>
        </div>
      </div>
    </q-expansion-item>
  </div>
</template>

<style scoped>
.panel {
  font-size: 14px;
}

.content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 12px;
  color: #757575;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.monospace {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.muted {
  color: #9e9e9e;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 0;
  color: #9e9e9e;
}

.empty p {
  margin: 0;
}

.classification {
  display: flex;
  gap: 12px;
}

.indicator {
  width: 18px;
  height: 18px;
  border-radius: 3px;
  flex-shrink: 0;
  margin-top: 2px;
}
</style>
