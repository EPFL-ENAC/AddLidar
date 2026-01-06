<template>
  <q-card
    flat
    class="card-flat cursor-pointer q-mb-md"
    :class="{
      'card-flat--selected': isSelected,
      'bg-blue-1': isHovered,
    }"
    @click="emit('click', mission.mission_key)"
    @mouseenter="emit('hover', mission.mission_key)"
    @mouseleave="emit('hover', null)"
  >
    <q-card-section class="q-py-sm q-px-md">
      <!-- Header: Name/Key + Status Badge (only if not success) -->
      <div class="row items-center no-wrap q-mb-xs">
        <div class="col row items-center no-wrap" style="min-width: 0">
          <div class="ellipsis text-subtitle1 text-weight-medium">
            {{ displayName }}
          </div>
          <q-badge
            v-if="showStatusBadge"
            :color="getStatusColor(mission.processing_status)"
            :label="formatStatus(mission.processing_status)"
            class="q-ml-sm"
          />
        </div>
        <q-badge
          v-if="mission.date"
          color="blue-grey-7"
          :label="formatMissionDate(mission.date)"
          class="q-ml-sm date-badge"
        />
      </div>

      <!-- Mission key subtitle (when name exists) -->
      <div
        v-if="mission.name"
        class="text-caption text-grey-6 ellipsis q-mb-xs"
        :title="mission.mission_key"
      >
        {{ mission.mission_key }}
      </div>

      <!-- Timestamps row - more explicit -->
      <div class="row q-gutter-x-lg text-caption q-mb-sm">
        <div v-if="mission.last_checked_time" class="column">
          <span class="text-grey-6">Checked</span>
          <span class="text-grey-8">{{
            formatDateTime(mission.last_checked_time)
          }}</span>
        </div>
        <div v-if="mission.last_processed_time" class="column">
          <span class="text-grey-6">Processed</span>
          <span class="text-grey-8">{{
            formatDateTime(mission.last_processed_time)
          }}</span>
        </div>
      </div>

      <!-- Metadata row (points & bounds) -->
      <div
        v-if="mission.metadata"
        class="row q-mb-sm text-caption q-gutter-x-md"
      >
        <div class="row items-center no-wrap">
          <q-icon name="scatter_plot" size="14px" class="q-mr-xs text-grey-6" />
          <span>{{ formatNumber(mission.metadata.points) }} pts</span>
        </div>
        <div
          v-if="mission.metadata.boundingBox"
          class="row items-center no-wrap"
        >
          <q-icon name="crop_free" size="14px" class="q-mr-xs text-grey-6" />
          <span>{{ formatBoundsCompact(mission.metadata.boundingBox) }}</span>
        </div>
      </div>

      <!-- Extra attributes -->
      <div v-if="parsedExtraAttributes" class="q-mb-sm">
        <!-- Description shown separately if long -->
        <div
          v-if="parsedExtraAttributes.description"
          class="text-caption text-grey-8 q-mb-xs"
          style="line-height: 1.4"
        >
          <q-icon name="notes" size="14px" class="q-mr-xs" />
          {{ parsedExtraAttributes.description }}
        </div>
        <!-- Other attributes as chips -->
        <div v-if="otherAttributes" class="row q-gutter-xs flex-wrap">
          <q-chip
            v-for="(value, key) in otherAttributes"
            :key="key"
            dense
            size="sm"
            color="grey-3"
            text-color="grey-8"
            class="extra-attr-chip"
          >
            <span class="text-weight-medium">{{ key }}:</span>
            <span class="q-ml-xs">{{ value }}</span>
          </q-chip>
        </div>
      </div>

      <!-- Action button -->
      <q-btn
        unelevated
        outline
        color="primary"
        label="Explore Point Cloud"
        icon="3d_rotation"
        size="sm"
        class="full-width"
        @click.stop="emit('view', mission.mission_key)"
      />
    </q-card-section>

    <!-- Error section (collapsible) -->
    <template v-if="mission.error_message">
      <q-separator />
      <q-card-section class="q-py-xs q-px-md">
        <q-expansion-item
          v-model="showErrorDetails"
          dense
          icon="error"
          header-class="text-negative q-pa-none"
        >
          <template #header>
            <q-item-section class="q-py-none">
              <q-item-label class="text-negative text-caption ellipsis">
                {{ mission.error_message }}
              </q-item-label>
            </q-item-section>
          </template>

          <div class="q-pa-sm">
            <div class="row items-center justify-between q-mb-xs">
              <span class="text-caption text-grey-8">Error Log</span>
              <q-btn
                flat
                dense
                size="xs"
                color="negative"
                icon="content_copy"
                :label="copyButtonText"
                @click.stop="copyErrorDetails"
                :disable="!mission.detailed_error_message"
              />
            </div>
            <pre v-if="mission.detailed_error_message" class="error-logs">{{
              formatDetailedError(mission.detailed_error_message)
            }}</pre>
            <div v-else class="text-caption text-grey-8">
              No detailed logs available.
            </div>
          </div>
        </q-expansion-item>
      </q-card-section>
    </template>
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

interface MissionMetadata {
  points?: number;
  boundingBox?: {
    min: [number, number];
    max: [number, number];
  };
}

interface Mission {
  mission_key: string;
  output_path?: string;
  processing_status: string;
  last_checked_time?: string | null;
  last_processed_time?: string | null;
  error_message?: string | null;
  detailed_error_message?: string | null;
  name?: string | null;
  date?: string | null;
  extra_attributes?: string | null;
  metadata?: MissionMetadata | null;
}

const emit = defineEmits<{
  click: [missionKey: string];
  hover: [missionKey: string | null];
  view: [missionKey: string];
}>();

const props = defineProps<{
  mission: Mission;
  isSelected?: boolean;
  isHovered?: boolean;
}>();

const displayName = computed(
  () => props.mission.name || props.mission.mission_key,
);

// Only show status badge if NOT success
const showStatusBadge = computed(() => {
  const status = props.mission.processing_status?.toLowerCase();
  return (
    status &&
    status !== "success" &&
    status !== "completed" &&
    status !== "processed"
  );
});

// Parse extra_attributes JSON
const parsedExtraAttributes = computed(() => {
  if (!props.mission.extra_attributes) return null;
  try {
    const parsed = JSON.parse(props.mission.extra_attributes);
    return Object.keys(parsed).length > 0 ? parsed : null;
  } catch {
    return null;
  }
});

// Other attributes excluding description (shown separately)
const otherAttributes = computed(() => {
  if (!parsedExtraAttributes.value) return null;
  const { description, ...rest } = parsedExtraAttributes.value;
  return Object.keys(rest).length > 0 ? rest : null;
});

function getStatusColor(status: string | undefined): string {
  if (!status) return "grey";
  switch (status.toLowerCase()) {
    case "completed":
    case "processed":
    case "success":
      return "positive";
    case "pending":
      return "warning";
    case "error":
    case "failed":
      return "negative";
    default:
      return "grey";
  }
}

const showErrorDetails = ref(false);
const copyButtonText = ref("Copy");

async function copyErrorDetails() {
  if (!props.mission.detailed_error_message) return;

  try {
    await navigator.clipboard.writeText(
      formatDetailedError(props.mission.detailed_error_message),
    );
    copyButtonText.value = "Copied!";
    setTimeout(() => {
      copyButtonText.value = "Copy";
    }, 2000);
  } catch (err) {
    console.error("Failed to copy error details:", err);
    copyButtonText.value = "Failed";
    setTimeout(() => {
      copyButtonText.value = "Copy";
    }, 2000);
  }
}

function formatStatus(status: string | undefined): string {
  if (!status) return "Unknown";
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function formatMissionDate(dateStr: string): string {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return dateStr;
  }
}

function formatDateTime(dateString: string | undefined): string {
  if (!dateString) return "N/A";
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / 86400000);

  // Show relative for recent, absolute for older
  if (diffDays === 0) {
    return `Today ${date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}`;
  } else if (diffDays === 1) {
    return `Yesterday ${date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  }
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function formatNumber(num: number | undefined): string {
  if (!num) return "0";
  if (num >= 1_000_000_000) return (num / 1_000_000_000).toFixed(1) + "B";
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
  if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
  return num.toString();
}

function formatBoundsCompact(
  boundingBox: { min: [number, number]; max: [number, number] } | undefined,
): string {
  if (!boundingBox) return "N/A";
  const { min, max } = boundingBox;
  const width = Math.abs(max[0] - min[0]);
  const height = Math.abs(max[1] - min[1]);
  return `${width.toFixed(0)}×${height.toFixed(0)}m`;
}

function formatDetailedError(detailedError: string | undefined): string {
  if (!detailedError) return "No detailed error information available.";
  return detailedError
    .replace(/\\n/g, "\n")
    .replace(/\\"/g, '"')
    .replace(/\\\\/g, "\\");
}
</script>

<style scoped>
.error-logs {
  font-family: monospace;
  font-size: 10px;
  margin: 0;
  padding: 6px;
  background: #f8fafc;
  border-radius: 4px;
  max-height: 150px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
