<template>
  <q-dialog v-model="showDialog" persistent>
    <q-card style="min-width: 350px; max-width: 500px">
      <q-card-section class="row items-center q-pb-none">
        <q-icon name="error" color="negative" size="md" class="q-mr-sm" />
        <div class="text-h6 text-weight-medium">Error</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="showDialog = false" />
      </q-card-section>

      <q-card-section>
        <div v-html="message" class="error-content"></div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Close" color="primary" @click="showDialog = false" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";

const props = defineProps<{
  message: string;
}>();

const showDialog = ref(false);

watch(
  () => props.message,
  (newMessage) => {
    showDialog.value = !!newMessage;
  },
  { immediate: true },
);
</script>

<style scoped>
.error-content :deep(a) {
  color: #c10015;
  text-decoration: underline;
}
</style>
