<template>
  <q-card
    bordered
    flat
    class="cursor-pointer transition q-mb-md"
    :class="{
      'bg-grey-3': isSelected,
    }"
    @click="emit('click', mission.mission_key)"
    @mouseenter="emit('hover', mission.mission_key)"
    @mouseleave="emit('hover', null)"
  >
    <q-card-section>
      <div class="row items-start q-mb-sm">
        <div class="col">
          <div class="text-h6">{{ mission.mission_key }}</div>
        </div>
        <div class="col-auto">
          <q-badge
            :color="getStatusColor(mission.processing_status)"
            :label="formatStatus(mission.processing_status)"
          />
        </div>
      </div>

      <q-list class="q-mb-sm">
        <q-item>
          <q-item-section avatar>
            <q-icon name="schedule" color="grey-6" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-grey-6">Last Checked</q-item-label>
            <q-item-label>{{
              formatDate(mission.last_checked_time)
            }}</q-item-label>
          </q-item-section>
        </q-item>

        <q-item v-if="mission.last_processed_time">
          <q-item-section avatar>
            <q-icon name="check_circle" color="primary" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-grey-6">Processed</q-item-label>
            <q-item-label>{{
              formatDate(mission.last_processed_time)
            }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>

      <div v-if="mission.metadata" class="q-mb-sm">
        <div class="row q-col-gutter-sm">
          <div class="col-6">
            <div class="text-grey-6">Points</div>
            <div>{{ formatNumber(mission.metadata.points) }}</div>
          </div>
          <div class="col-6">
            <div class="text-grey-6">Bounds</div>
            <div>{{ formatBounds(mission.metadata.boundingBox) }}</div>
          </div>
        </div>
      </div>

      <q-btn
        outline
        color="primary"
        label="View"
        icon="visibility"
        class="full-width q-mt-sm"
        @click.stop="emit('view', mission.mission_key)"
      />
    </q-card-section>

    <q-separator v-if="mission.error_message" />

    <q-card-section v-if="mission.error_message">
      <q-expansion-item
        v-model="showErrorDetails"
        icon="error"
        header-class="text-negative"
      >
        <template v-slot:header>
          <q-item-section>
            <q-item-label class="text-negative">
              {{ mission.error_message }}
            </q-item-label>
          </q-item-section>
        </template>

        <div class="q-mt-sm">
          <div class="row items-center justify-between q-mb-sm">
            <div>Error Log</div>
            <q-btn
              flat
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
          <div v-else class="text-caption text-grey-7">
            No detailed logs available.
          </div>
        </div>
      </q-expansion-item>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref } from "vue";

interface Mission {
  mission_key: string;
  output_path: string;
  processing_status: string;
  last_checked_time: string;
  last_processed_time?: string;
  error_message?: string;
  detailed_error_message?: string;
  metadata?: {
    points: number;
    boundingBox: {
      min: [number, number];
      max: [number, number];
    };
  };
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

function getStatusColor(status: string | undefined): string {
  if (!status) return "grey";
  switch (status.toLowerCase()) {
    case "completed":
    case "processed":
      return "positive";
    case "pending":
      return "warning";
    case "error":
      return "negative";
    default:
      return "grey";
  }
}

// Reactive state for error details expansion
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

function formatDate(dateString: string | undefined): string {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleString();
}

function formatNumber(num: number | undefined): string {
  if (!num) return "N/A";
  return new Intl.NumberFormat().format(num);
}

function formatBounds(
  boundingBox: { min: [number, number]; max: [number, number] } | undefined,
): string {
  if (!boundingBox) return "N/A";
  const { min, max } = boundingBox;
  return `[${min[0].toFixed(1)}, ${min[1].toFixed(1)}] to [${max[0].toFixed(
    1,
  )}, ${max[1].toFixed(1)}]`;
}

function formatDetailedError(detailedError: string | undefined): string {
  if (!detailedError) return "No detailed error information available.";

  // Replace \\n with actual newlines for better readability
  return detailedError
    .replace(/\\n/g, "\n")
    .replace(/\\"/g, '"')
    .replace(/\\\\/g, "\\");
}
</script>

<style scoped>
.error-logs {
  font-family: monospace;
  font-size: 11px;
  margin: 0;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
