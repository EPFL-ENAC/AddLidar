<script setup lang="ts">
const emit = defineEmits<{
  close: [];
}>();

const features = [
  {
    icon: "flight",
    title: "Browse Missions",
    description:
      "Explore airborne LiDAR missions with interactive map footprints",
  },
  {
    icon: "3d_rotation",
    title: "3D Visualization",
    description:
      "View point clouds colored by elevation, intensity, classification, and more",
  },
  {
    icon: "download",
    title: "Export Data",
    description: "Download custom subsets with format conversion and filtering",
  },
];

const formats = ["LAS", "LAZ", "PCD"];
const projections = ["EPSG:4326", "EPSG:3857", "EPSG:2056"];
</script>

<template>
  <div class="q-pa-md overflow-auto" style="max-width: 700px; padding-top: 0px">
    <!-- Features -->
    <div
      class="row q-col-gutter-sm q-col-gutter-md-md q-col-gutter-lg-lg q-mb-lg q-mb-xl-lg"
    >
      <p class="text-body2 text-grey-8">
        A web platform for storing, processing, and visualizing LiDAR datasets
        collected from airborne missions.
      </p>
      <div v-for="feature in features" :key="feature.icon" class="col-12">
        <q-card flat bordered class="full-height">
          <q-card-section class="text-center q-pa-sm q-pa-md-md">
            <div class="text-subtitle2 q-mt-xs">
              <q-icon
                :name="feature.icon"
                size="28px"
                class="q-icon-size-md-36 q-pr-sm q-pr-md-md"
              />{{ feature.title }}
            </div>
            <div class="text-caption text-grey-6 q-mt-xs">
              {{ feature.description }}
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Capabilities -->
    <div class="q-pt-md q-mb-lg q-mb-xl-lg">
      <div class="text-subtitle2 text-uppercase text-weight-medium q-mb-sm">
        Processing Capabilities
      </div>
      <p class="text-body2 text-grey-8">
        Export point cloud subsets with on-demand processing: apply density
        filtering, define regions of interest using 3D clip volumes, and
        transform coordinates between reference systems.
      </p>

      <div class="row q-col-gutter-sm q-col-gutter-md-md q-mt-sm q-mt-md-md">
        <div class="col-12 col-sm-6">
          <div class="text-caption text-grey-6 q-mb-xs">Supported Formats</div>
          <q-chip
            v-for="format in formats"
            :key="format"
            size="sm"
            color="primary"
            text-color="white"
            class="q-mr-xs q-mb-xs"
          >
            {{ format }}
          </q-chip>
        </div>
        <div class="col-12 col-sm-6">
          <div class="text-caption text-grey-6 q-mb-xs">Projections</div>
          <q-chip
            v-for="proj in projections"
            :key="proj"
            size="sm"
            outline
            color="primary"
            class="q-mr-xs q-mb-xs"
          >
            {{ proj }}
          </q-chip>
        </div>
      </div>
    </div>

    <!-- Context -->
    <div class="q-pt-md q-mb-lg q-mb-xl-lg">
      <div class="text-subtitle2 text-uppercase text-weight-medium q-mb-sm">
        Research Context
      </div>
      <p class="text-body2 text-grey-8">
        Built to support research at EPFL's ESO laboratory, AddLidar provides an
        efficient pipeline for managing large-scale LiDAR datasets. The platform
        handles datasets exceeding 100GB with automated processing and
        web-optimized visualization.
      </p>
    </div>

    <q-separator class="q-my-md q-my-lg-lg" />

    <!-- Credits -->
    <div class="text-left text-caption text-grey-8">
      <div>
        Developed by
        <a
          href="https://www.epfl.ch/labs/eso/"
          target="_blank"
          rel="noopener"
          class="text-primary"
        >
          EPFL ESO
        </a>
        &
        <a
          href="https://www.epfl.ch/schools/enac/about/data-at-enac/enac-it4research/"
          target="_blank"
          rel="noopener"
          class="text-primary"
        >
          ENAC-IT4Research
        </a>
      </div>
      <div class="q-pt-sm">
        <a
          href="https://github.com/EPFL-ENAC/AddLidar"
          target="_blank"
          rel="noopener"
          class="text-primary"
        >
          <q-icon name="code" size="16px" />
          Code is Open Source (GPL-3.0)
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Responsive icon size */
.q-icon-size-md-36 {
  font-size: 28px;
}

@media (min-width: 1024px) {
  .q-icon-size-md-36 {
    font-size: 36px;
  }
}
</style>
