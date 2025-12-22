<script setup lang="ts">
import DefaultLayout from "@/layouts/DefaultLayout.vue";
</script>

<template>
  <default-layout>
    <q-page class="flex flex-center">
      <div class="text-center q-pa-xl" style="max-width: 600px">
        <q-icon name="terrain" color="primary" size="80px" class="q-mb-lg" />

        <h1 class="text-h4 text-weight-medium q-mb-md">About AddLidar</h1>

        <p class="text-body1 text-grey-7 q-mb-lg">
          AddLidar is a web application for exploring and exporting LiDAR point
          cloud data. Browse available missions, visualize point clouds in 3D,
          and export subsets of data in various formats.
        </p>

        <div class="q-gutter-md">
          <div class="row items-center justify-center q-gutter-x-lg">
            <div class="text-center">
              <q-icon name="explore" size="32px" color="primary" />
              <div class="text-caption text-grey-6 q-mt-xs">
                Browse Missions
              </div>
            </div>
            <div class="text-center">
              <q-icon name="3d_rotation" size="32px" color="primary" />
              <div class="text-caption text-grey-6 q-mt-xs">
                3D Visualization
              </div>
            </div>
            <div class="text-center">
              <q-icon name="download" size="32px" color="primary" />
              <div class="text-caption text-grey-6 q-mt-xs">Export Data</div>
            </div>
          </div>
        </div>

        <q-separator class="q-my-xl" />

        <div class="text-caption text-grey-5">Developed by EPFL-ENAC</div>
      </div>
    </q-page>
  </default-layout>
</template>
