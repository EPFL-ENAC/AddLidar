<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import EPFLLogo from "@/assets/EPFL_Logo.svg";

interface NavItem {
  label: string;
  to: string;
  icon?: string;
}

interface Props {
  showBackButton?: boolean;
  subtitle?: string;
  showSidebarToggle?: boolean;
  sidebarOpen?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showBackButton: false,
  showSidebarToggle: false,
  sidebarOpen: false,
});

const emit = defineEmits<{
  back: [];
  toggleSidebar: [];
}>();

const router = useRouter();

const navItems: NavItem[] = [
  { label: "Missions", to: "/", icon: "explore" },
  { label: "About", to: "/about", icon: "info" },
];

const currentRoute = computed(() => router.currentRoute.value.path);

const handleBack = () => {
  emit("back");
};

const handleToggleSidebar = () => {
  emit("toggleSidebar");
};
</script>

<template>
  <q-header class="app-header bg-white text-dark" elevated>
    <q-toolbar class="q-px-md">
      <q-btn
        v-if="showBackButton"
        flat
        round
        icon="arrow_back"
        color="grey-8"
        @click="handleBack"
      >
        <q-tooltip>Back to missions</q-tooltip>
      </q-btn>

      <q-toolbar-title class="row items-center q-gutter-sm">
        <img :src="EPFLLogo" alt="EPFL" class="epfl-logo" />
        <q-separator vertical inset class="q-mx-xs" />
        <q-icon name="terrain" color="primary" size="24px" />
        <span class="text-h6 text-weight-medium">AddLidar</span>
        <template v-if="subtitle">
          <q-separator vertical inset class="q-mx-xs" />
          <span
            class="text-body2 text-grey-7 ellipsis"
            style="max-width: 300px"
          >
            {{ subtitle }}
          </span>
        </template>
      </q-toolbar-title>

      <q-tabs
        :model-value="currentRoute"
        inline-label
        class="text-grey-8 q-mx-md"
        active-color="primary"
        indicator-color="primary"
        dense
      >
        <q-route-tab
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :icon="item.icon"
          :label="item.label"
          class="q-px-md"
        />
      </q-tabs>

      <q-btn
        v-if="showSidebarToggle"
        flat
        round
        :icon="sidebarOpen ? 'menu_open' : 'menu'"
        color="grey-8"
        @click="handleToggleSidebar"
      >
        <q-tooltip>{{ sidebarOpen ? "Hide" : "Show" }} sidebar</q-tooltip>
      </q-btn>
    </q-toolbar>
  </q-header>
</template>

<style scoped>
.epfl-logo {
  height: 24px;
  width: auto;
}

.app-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}
</style>
