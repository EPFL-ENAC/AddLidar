<script setup lang="ts">
import { ref } from "vue";
import AboutContent from "@/components/AboutContent.vue";

interface Props {
  showBackButton?: boolean;
  subtitle?: string;
}

const props = withDefaults(defineProps<Props>(), {
  showBackButton: false,
});

const emit = defineEmits<{
  back: [];
}>();

const showAbout = ref(false);

function handleBack() {
  emit("back");
}

function toggleAbout() {
  showAbout.value = !showAbout.value;
}
</script>

<template>
  <div class="row" style="height: 100vh; width: 100vw">
    <!-- Left Sidebar -->
    <aside class="column bg-white sidebar-panel">
      <!-- Header -->
      <header class="q-px-lg q-py-lg q-py-lg-lg q-py-xl-xl">
        <div class="row items-center justify-between">
          <q-btn
            flat
            round
            dense
            icon="arrow_back"
            color="grey-8"
            size="sm"
            :style="{ visibility: showBackButton ? 'visible' : 'hidden' }"
            @click="handleBack"
          >
            <q-tooltip v-if="showBackButton">Back to missions</q-tooltip>
          </q-btn>

          <div class="col row items-center justify-center">
            <div class="row items-center q-px-sm">
              <q-icon name="view_in_ar" color="primary" size="24px" />
              <span class="text-h5">AddLidar</span>
            </div>
            <q-separator vertical size="2px" inset />
            <img
              class="q-px-sm"
              src="@/assets/EPFL_Logo.svg"
              alt="AddLidar"
              style="height: 24px; width: auto"
            />
          </div>

          <q-btn
            flat
            round
            dense
            :icon="showAbout ? 'close' : 'info_outline'"
            color="grey-8"
            size="sm"
            @click="toggleAbout"
          >
            <q-tooltip>{{ showAbout ? "Close" : "About" }}</q-tooltip>
          </q-btn>
        </div>
      </header>
      <q-separator />
      <!-- Sidebar Content -->
      <div class="col overflow-auto column sidebar-scrollable">
        <about-content v-if="showAbout" />
        <template v-else>
          <!-- Mission Name Title -->
          <div v-if="subtitle" class="q-px-lg q-py-md q-py-xl-lg">
            <div class="row items-center justify-between">
              <div
                class="text-overline text-grey-6"
                style="letter-spacing: 0.5px"
              >
                SELECTED MISSION
              </div>
              <div class="text-h6 text-weight-medium ellipsis">
                {{ subtitle }}
              </div>
            </div>
          </div>

          <q-separator v-if="subtitle" />

          <div class="col column overflow-hidden">
            <slot name="sidebar" />
          </div>
        </template>
      </div>
    </aside>

    <!-- Right Content Panel -->
    <main class="col column bg-grey-2 content-panel">
      <slot name="content" />
    </main>
  </div>
</template>

<style scoped>
.sidebar-panel {
  width: 550px;
  min-width: 550px;
  max-height: 100vh;
  border-right: 1px solid rgba(0, 0, 0, 0.08);
  overflow: hidden;
  background: rgb(187, 126, 46);
}

.content-panel {
  overflow: hidden;
}

/* Modern minimalist scrollbar */
.sidebar-scrollable {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
  min-height: 0;
}

.sidebar-scrollable::-webkit-scrollbar {
  width: 6px;
}

.sidebar-scrollable::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-scrollable::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.sidebar-scrollable::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

@media (max-width: 1200px) {
  .sidebar-panel {
    width: 450px;
    min-width: 450px;
  }
}

@media (max-width: 768px) {
  .sidebar-panel {
    width: 100%;
    min-width: 0;
    border-right: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    max-height: 50vh;
  }
}
</style>
