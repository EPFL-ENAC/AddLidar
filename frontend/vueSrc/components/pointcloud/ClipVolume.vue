<template>
  <div>
    <div class="q-mb-sm text-grey-8">Clip Volume</div>
    <q-btn
      v-if="!item"
      outline
      label="Insert Volume"
      color="primary"
      icon="add_box"
      class="full-width q-mb-md"
      @click="startInsertion"
    />
    <q-btn
      v-else
      outline
      label="Remove Volume"
      color="negative"
      icon="delete"
      class="full-width q-mb-md"
      @click="removeClipVolume"
    />

    <div v-if="item" class="q-gutter-y-sm">
      <div>
        <div class="text-grey-6 q-mb-xs">Position</div>
        <div>
          X: {{ position.x.toFixed(2) }} • Y: {{ position.y.toFixed(2) }} • Z:
          {{ position.z.toFixed(2) }}
        </div>
      </div>

      <div>
        <div class="text-grey-6 q-mb-xs">Scale</div>
        <div>
          X: {{ scale.x.toFixed(2) }} • Y: {{ scale.y.toFixed(2) }} • Z:
          {{ scale.z.toFixed(2) }}
        </div>
      </div>

      <div>
        <div class="text-grey-6 q-mb-xs">Rotation</div>
        <div>
          X: {{ ((rotation.x * 180) / Math.PI).toFixed(1) }}° • Y:
          {{ ((rotation.y * 180) / Math.PI).toFixed(1) }}° • Z:
          {{ ((rotation.z * 180) / Math.PI).toFixed(1) }}°
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useExportJobStore } from "@/stores/exportJobStore";
import { nextTick, ref } from "vue";

const exportJobStore = useExportJobStore();
const {
  clipPosition: position,
  clipRotation: rotation,
  clipScale: scale,
} = exportJobStore;

const item = ref<any>(null);

function startInsertion() {
  const volumeTool = exportJobStore.volumeTool;
  if (!volumeTool || !volumeTool.startInsertion) return;

  // Start insertion and get the created item
  item.value = volumeTool.startInsertion({ clip: true });

  // Use nextTick to ensure the DOM has updated
  nextTick(() => {
    try {
      // Use type assertion for jQuery plugin
      let measurementsRoot = ($("#jstree_scene") as any)
        .jstree()
        .get_json("measurements");
      let jsonNode = measurementsRoot.children.find(
        (child: any) => child.data.uuid === item.value.uuid,
      );
      ($("#jstree_scene") as any).jstree("deselect_all");
      ($("#jstree_scene") as any).jstree("select_node", jsonNode.id);
      onVolumeAdded({
        volume: item.value,
      });
    } catch (error) {
      console.error("Error selecting clip volume in jstree:", error);
    }
  });
}

function removeClipVolume() {
  item.value.removeEventListener("scale_changed", onClipChanged);
  item.value.removeEventListener("orientation_changed", onClipChanged);
  item.value.removeEventListener("position_changed", onClipChanged);
  item.value.removeEventListener("deselect", onClipChanged);
  item.value = null;
  (window as any).viewer.scene.removeAllClipVolumes();
  exportJobStore.resetClipVolume();
}

function onClipChanged({ object }: { object: any }) {
  exportJobStore.setClipPosition(object.position);
  exportJobStore.setClipRotation(object.rotation.toVector3());
  exportJobStore.setClipScale(object.scale);
}

function onVolumeAdded({ volume }: { volume: any }) {
  exportJobStore.setClipVolume(volume);
  volume.addEventListener("scale_changed", onClipChanged);
  volume.addEventListener("orientation_changed", onClipChanged);
  volume.addEventListener("position_changed", onClipChanged);
  setTimeout(() => onClipChanged({ object: volume }), 5000);
}
</script>
