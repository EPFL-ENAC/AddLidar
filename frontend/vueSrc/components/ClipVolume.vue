<template>
  <q-expansion-item label="Clip Volume" bordered default-opened>
    <q-card>
      <q-card-section>
        <q-btn
          v-if="!item"
          label="Insert volume"
          color="secondary"
          outline
          class="q-mt-md full-width"
          @click="startInsertion"
        />
        <q-btn
          v-else
          label="Remove volume"
          color="negative"
          outline
          class="q-mt-md full-width"
          @click="removeClipVolume"
        />
      </q-card-section>
      <q-card-section v-if="item">
        <div class="text-subtitle2 q-mb-sm">Position X,Y,Z</div>
        <div class="row q-mb-sm">
          <div class="col">
            <q-badge color="blue" flat>{{ position.x.toFixed() }}</q-badge>
          </div>
          <div class="col">
            <q-badge color="green" flat>{{ position.y.toFixed() }}</q-badge>
          </div>
          <div class="col">
            <q-badge color="red" flat>{{ position.z.toFixed() }}</q-badge>
          </div>
        </div>
        <div class="text-subtitle2 q-mb-sm">Scale X,Y,Z</div>
        <div class="row">
          <div class="col">
            <q-badge color="blue" flat>{{ scale.x.toFixed(2) }}</q-badge>
          </div>
          <div class="col">
            <q-badge color="green" flat>{{ scale.y.toFixed(2) }}</q-badge>
          </div>
          <div class="col">
            <q-badge color="red" flat>{{ scale.z.toFixed(2) }}</q-badge>
          </div>
        </div>
        <div class="text-subtitle2 q-mb-sm">Rotation X,Y,Z (deg)</div>
        <div class="row q-mb-sm">
          <div class="col">
            <q-badge color="blue" flat
              >{{ ((rotation.x * 180) / Math.PI).toFixed(1) }}°</q-badge
            >
          </div>
          <div class="col">
            <q-badge color="green" flat
              >{{ ((rotation.y * 180) / Math.PI).toFixed(1) }}°</q-badge
            >
          </div>
          <div class="col">
            <q-badge color="red" flat
              >{{ ((rotation.z * 180) / Math.PI).toFixed(1) }}°</q-badge
            >
          </div>
        </div>
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { usePointCloudStore } from "@/stores/pointcloud";
import { nextTick, ref } from "vue";

const store = usePointCloudStore();
const {
  clipPosition: position,
  clipRotation: rotation,
  clipScale: scale,
} = store;

const item = ref<any>(null);

function startInsertion() {
  const volumeTool = store.volumeTool;
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
        (child: any) => child.data.uuid === item.value.uuid
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
  store.resetClipVolume();
}

function onClipChanged({ object }: { object: any }) {
  store.setClipPosition(object.position);
  store.setClipRotation(object.rotation.toVector3());
  store.setClipScale(object.scale);
}

function onVolumeAdded({ volume }: { volume: any }) {
  console.log("Volume added", volume);
  store.setClipVolume(volume);
  volume.addEventListener("scale_changed", onClipChanged);
  volume.addEventListener("orientation_changed", onClipChanged);
  volume.addEventListener("position_changed", onClipChanged);
  setTimeout(() => onClipChanged({ object: volume }), 5000);
}
</script>

<style scoped>
.row {
  display: flex;
  flex-wrap: wrap;
  margin-left: -12px;
  margin-right: -12px;
}

.col {
  flex-basis: 0;
  flex-grow: 1;
  max-width: 100%;
  text-align: center;
  padding: 0 8px;
}

.q-badge {
  width: 100%;
}
</style>
