<script setup lang="ts">
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
  <div class="q-pa-xl overflow-auto" style="max-width: 700px">
    <div class="text-center q-mb-xl">
      <h1 class="text-h4 text-weight-medium q-mb-md">
        About AddLidar <q-icon name="view_in_ar" color="primary" size="36px" />
      </h1>
      <p class="text-body1 text-grey-7">
        A web platform for storing, processing, and visualizing LiDAR datasets
        collected from airborne missions.
      </p>
    </div>

    <!-- Features -->
    <div class="row q-col-gutter-lg q-mb-xl">
      <div v-for="feature in features" :key="feature.icon" class="col-12">
        <q-card flat bordered class="full-height">
          <q-card-section class="text-center">
            <q-icon :name="feature.icon" size="40px" color="primary" />
            <div class="text-subtitle1 text-weight-medium q-mt-sm">
              {{ feature.title }}
            </div>
            <div class="text-caption text-grey-6 q-mt-xs">
              {{ feature.description }}
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Capabilities -->
    <div class="q-mb-xl">
      <div class="text-subtitle1 text-weight-medium q-mb-sm">
        Processing Capabilities
      </div>
      <p class="text-body2 text-grey-7">
        Export point cloud subsets with on-demand processing: apply density
        filtering, define regions of interest using 3D clip volumes, and
        transform coordinates between reference systems.
      </p>

      <div class="row q-col-gutter-md q-mt-md">
        <div class="col-6">
          <div class="text-caption text-grey-6 q-mb-xs">Supported Formats</div>
          <q-chip
            v-for="format in formats"
            :key="format"
            size="sm"
            color="primary"
            text-color="white"
            class="q-mr-xs"
          >
            {{ format }}
          </q-chip>
        </div>
        <div class="col-6">
          <div class="text-caption text-grey-6 q-mb-xs">Projections</div>
          <q-chip
            v-for="proj in projections"
            :key="proj"
            size="sm"
            outline
            color="primary"
            class="q-mr-xs"
          >
            {{ proj }}
          </q-chip>
        </div>
      </div>
    </div>

    <!-- Context -->
    <div class="q-mb-xl">
      <div class="text-subtitle1 text-weight-medium q-mb-sm">
        Research Context
      </div>
      <p class="text-body2 text-grey-7">
        Built to support research at EPFL's ESO laboratory, AddLidar provides an
        efficient pipeline for managing large-scale LiDAR datasets. The platform
        handles datasets exceeding 100GB with automated processing and
        web-optimized visualization.
      </p>
    </div>

    <q-separator class="q-my-lg" />

    <!-- Credits -->
    <div class="text-center">
      <div class="text-caption text-grey-5 q-mb-sm">
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
      <div class="text-caption text-grey-5">
        <a
          href="https://github.com/EPFL-ENAC/AddLidar"
          target="_blank"
          rel="noopener"
          class="text-grey-6"
        >
          <q-icon name="mdi-github" size="16px" class="q-mr-xs" />
          Open Source (GPL-3.0)
        </a>
      </div>
    </div>
  </div>
</template>
