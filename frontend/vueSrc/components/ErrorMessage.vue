<template>
  <div v-if="message" class="error-message" v-html="message"></div>
</template>

<script setup>
const props = defineProps({
  message: {
    type: String,
    default: "",
  },
});
</script>

<style scoped>
.error-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgb(255, 255, 255);
  padding: 1em;
  border: 2px solid rgb(185, 54, 54);
  border-radius: 1rem;
  max-width: 400px;
  z-index: 10;
}

.error-message:deep(a) {
  color: rgb(185, 54, 54) !important;
}
</style>
