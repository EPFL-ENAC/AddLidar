<template>
  <div
    class="mission-card"
    :class="{
      'mission-pending': mission.processing_status === 'pending',
      'mission-selected': isSelected,
      'mission-hovered': isHovered,
    }"
    @click="$emit('click', mission.mission_key)"
    @mouseenter="$emit('hover', mission.mission_key)"
    @mouseleave="$emit('hover', null)"
  >
    <div class="mission-status">
      <span
        class="status-badge"
        :class="`status-${mission.processing_status || 'unknown'}`"
      >
        {{ formatStatus(mission.processing_status) }}
      </span>
    </div>

    <div class="mission-info">
      <h3>{{ mission.mission_key }}</h3>
      <p class="mission-details">
        <strong>Output:</strong> {{ mission.output_path }}<br />
        <strong>Last Checked:</strong>
        {{ formatDate(mission.last_checked_time) }}<br />
        <span v-if="mission.last_processed_time">
          <strong>Processed:</strong>
          {{ formatDate(mission.last_processed_time) }}
        </span>
        <span v-else> <strong>Status:</strong> Not yet processed </span>
      </p>

      <div v-if="mission.metadata" class="metadata-info">
        <p>
          <strong>Points:</strong> {{ formatNumber(mission.metadata.points)
          }}<br />
          <strong>Bounds:</strong>
          {{ formatBounds(mission.metadata.boundingBox) }}
        </p>
      </div>

      <div class="mission-actions">
        <button
          class="view-btn"
          @click.stop="$emit('view', mission.mission_key)"
        >
          View Mission
        </button>
      </div>
    </div>

    <div v-if="mission.error_message" class="error-message">
      <div class="error-header" @click="toggleErrorDetails">
        <span><strong>Error:</strong> {{ mission.error_message }}</span>
        <span class="error-toggle">
          <i :class="showErrorDetails ? 'arrow-up' : 'arrow-down'"></i>
          {{ showErrorDetails ? "Hide Details" : "Show Details" }}
        </span>
      </div>
      <div
        v-if="showErrorDetails && mission.detailed_error_message"
        class="error-details"
      >
        <div class="error-details-header">
          <strong>Detailed Logs:</strong>
          <button
            class="copy-btn"
            @click.stop="copyErrorDetails"
            :disabled="!mission.detailed_error_message"
          >
            {{ copyButtonText }}
          </button>
        </div>
        <pre class="error-logs">{{
          formatDetailedError(mission.detailed_error_message)
        }}</pre>
      </div>
      <div
        v-else-if="showErrorDetails && !mission.detailed_error_message"
        class="error-details"
      >
        <p class="no-details">No detailed error logs available.</p>
      </div>
    </div>
  </div>
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

defineEmits<{
  click: [missionKey: string];
  hover: [missionKey: string | null];
  view: [missionKey: string];
}>();

// Reactive state for error details expansion
const showErrorDetails = ref(false);
const copyButtonText = ref("Copy");

// Get props reference for access in functions
const props = defineProps<{
  mission: Mission;
  isSelected?: boolean;
  isHovered?: boolean;
}>();

function toggleErrorDetails() {
  showErrorDetails.value = !showErrorDetails.value;
}

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
.mission-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s,
    border-color 0.2s;
  background: white;
  position: relative;
  margin-bottom: 15px;
}

.mission-card:hover:not(.mission-pending) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.mission-card.mission-selected {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.mission-card.mission-hovered {
  border-color: #6c757d;
}

.mission-pending {
  opacity: 0.7;
}

.mission-status {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.status-pending {
  background: #ff9800;
  color: white;
}

.status-completed,
.status-processed {
  background: #4caf50;
  color: white;
}

.status-error {
  background: #f44336;
  color: white;
}

.status-unknown {
  background: #9e9e9e;
  color: white;
}

.mission-info {
  padding: 15px;
  padding-top: 35px; /* Account for status badge */
}

.mission-info h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
}

.mission-details {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 13px;
  line-height: 1.4;
}

.metadata-info {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.metadata-info p {
  margin: 0;
  font-size: 12px;
  color: #555;
}

.mission-actions {
  text-align: right;
}

.view-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 12px;
}

.view-btn:hover:not(:disabled) {
  background: #0056b3;
}

.view-btn:disabled {
  background: #ccc;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  border-top: 1px solid #ffcdd2;
  font-size: 12px;
}

.error-header {
  padding: 10px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s;
}

.error-header:hover {
  background: #ffcdd2;
}

.error-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #ad1457;
  font-weight: normal;
}

.arrow-down::before {
  content: "▼";
  font-size: 10px;
}

.arrow-up::before {
  content: "▲";
  font-size: 10px;
}

.error-details {
  border-top: 1px solid #ffcdd2;
  background: #fce4ec;
}

.error-details-header {
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f8bbd9;
}

.copy-btn {
  background: #e91e63;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 10px;
  transition: background-color 0.2s;
}

.copy-btn:hover:not(:disabled) {
  background: #c2185b;
}

.copy-btn:disabled {
  background: #f8bbd9;
  cursor: not-allowed;
}

.error-logs {
  padding: 10px;
  margin: 0;
  background: #fff;
  border: 1px solid #f8bbd9;
  border-radius: 4px;
  margin: 10px;
  max-height: 300px;
  overflow-y: auto;
  font-family: "Courier New", monospace;
  font-size: 11px;
  line-height: 1.4;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}

.no-details {
  padding: 10px;
  margin: 0;
  font-style: italic;
  color: #999;
}
</style>
