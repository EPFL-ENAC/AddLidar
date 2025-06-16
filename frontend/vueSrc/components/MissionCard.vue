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
      <strong>Error:</strong> {{ mission.error_message }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface Mission {
  mission_key: string;
  output_path: string;
  processing_status: string;
  last_checked_time: string;
  last_processed_time?: string;
  error_message?: string;
  metadata?: {
    points: number;
    boundingBox: {
      min: [number, number];
      max: [number, number];
    };
  };
}

defineProps<{
  mission: Mission;
  isSelected?: boolean;
  isHovered?: boolean;
}>();

defineEmits<{
  click: [missionKey: string];
  hover: [missionKey: string | null];
  view: [missionKey: string];
}>();

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
  padding: 10px;
  border-top: 1px solid #ffcdd2;
  font-size: 12px;
}
</style>
