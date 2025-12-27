<template>
  <div class="expanded-details-container q-pa-md q-pl-lg">
    <!-- Metadata details -->
    <div v-if="mission.metadata" class="q-mb-md">
      <div class="text-body2 text-grey-8 text-wrap">
        {{ formatNumber(mission.metadata.points) }} points
        <span v-if="mission.metadata.boundingBox" class="q-ml-md">
          {{ formatBoundsCompact(mission.metadata.boundingBox) }}
        </span>
      </div>
    </div>

    <!-- Description -->
    <div
      v-if="parsedExtraAttributes?.description"
      class="text-body2 text-grey-8 q-mb-md text-wrap"
    >
      {{ parsedExtraAttributes.description }}
    </div>

    <!-- Other attributes -->
    <div v-if="otherAttributes" class="q-mb-md">
      <div
        v-for="(value, key) in otherAttributes"
        :key="key"
        class="text-body2 text-grey-8 text-wrap"
      >
        <span class="text-weight-medium">{{ key }}:</span> {{ value }}
      </div>
    </div>

    <!-- Timestamps -->
    <div
      v-if="mission.last_checked_time || mission.last_processed_time"
      class="q-mb-md"
    >
      <div
        v-if="mission.last_checked_time"
        class="text-body2 text-grey-7 text-wrap"
      >
        Last checked: {{ formatDateTime(mission.last_checked_time) }}
      </div>
      <div
        v-if="mission.last_processed_time"
        class="text-body2 text-grey-7 text-wrap"
      >
        Last processed: {{ formatDateTime(mission.last_processed_time) }}
      </div>
    </div>

    <!-- Error message -->
    <div v-if="mission.error_message" class="q-mb-md">
      <div class="text-body2 text-negative q-mb-sm text-wrap">
        {{ mission.error_message }}
      </div>
      <q-btn
        v-if="mission.detailed_error_message"
        flat
        dense
        size="sm"
        color="grey-7"
        icon="content_copy"
        label="Copy error log"
        @click.stop="copyToClipboard"
      />
    </div>

    <!-- Actions -->
    <div class="row justify-end">
      <q-btn
        v-if="isProcessed"
        flat
        color="primary"
        label="Explore"
        icon-right="arrow_forward"
        size="sm"
        @click="$emit('explore', mission.mission_key)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface MissionMetadata {
  points?: number;
  boundingBox?: {
    min: [number, number];
    max: [number, number];
  };
}

interface Mission {
  mission_key: string;
  name?: string | null;
  date?: string | null;
  processing_status: string;
  last_checked_time?: string | null;
  last_processed_time?: string | null;
  error_message?: string | null;
  detailed_error_message?: string | null;
  extra_attributes?: string | null;
  metadata?: MissionMetadata | null;
}

const props = defineProps<{
  mission: Mission;
}>();

const emit = defineEmits<{
  explore: [missionKey: string];
}>();

const isProcessed = computed(() => {
  const status = props.mission.processing_status?.toLowerCase();
  return (
    status === "completed" || status === "processed" || status === "success"
  );
});

const parsedExtraAttributes = computed(() => {
  if (!props.mission.extra_attributes) return null;
  try {
    const parsed = JSON.parse(props.mission.extra_attributes);
    return Object.keys(parsed).length > 0 ? parsed : null;
  } catch {
    return null;
  }
});

const otherAttributes = computed(() => {
  if (!parsedExtraAttributes.value) return null;
  const { description, ...rest } = parsedExtraAttributes.value;
  return Object.keys(rest).length > 0 ? rest : null;
});

const formattedDetailedError = computed(() => {
  if (!props.mission.detailed_error_message)
    return "No detailed error information available.";
  return props.mission.detailed_error_message
    .replace(/\\n/g, "\n")
    .replace(/\\"/g, '"')
    .replace(/\\\\/g, "\\");
});

function formatNumber(num: number | undefined): string {
  if (!num) return "0";
  if (num >= 1_000_000_000) return (num / 1_000_000_000).toFixed(1) + "B";
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
  if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
  return num.toString();
}

function formatBoundsCompact(boundingBox: {
  min: [number, number];
  max: [number, number];
}): string {
  const { min, max } = boundingBox;
  const width = Math.abs(max[0] - min[0]);
  const height = Math.abs(max[1] - min[1]);
  return `${width.toFixed(0)}×${height.toFixed(0)}m`;
}

function formatDateTime(dateString: string | undefined): string {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(formattedDetailedError.value);
  } catch (err) {
    console.error("Failed to copy to clipboard:", err);
  }
}
</script>

<style scoped>
.expanded-details-container {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

.text-wrap {
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
  white-space: normal;
}

.error-logs {
  font-family: monospace;
  font-size: 11px;
  margin: 0;
  padding: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
