<script setup lang="ts">
import { useMeta } from "quasar";

useMeta({
  link: {
    appleIcon57: {
      rel: "apple-touch-icon",
      sizes: "57x57",
      href: "/favicons/apple-icon-57x57.png",
    },
    appleIcon60: {
      rel: "apple-touch-icon",
      sizes: "60x60",
      href: "/favicons/apple-icon-60x60.png",
    },
    appleIcon72: {
      rel: "apple-touch-icon",
      sizes: "72x72",
      href: "/favicons/apple-icon-72x72.png",
    },
    appleIcon76: {
      rel: "apple-touch-icon",
      sizes: "76x76",
      href: "/favicons/apple-icon-76x76.png",
    },
    appleIcon114: {
      rel: "apple-touch-icon",
      sizes: "114x114",
      href: "/favicons/apple-icon-114x114.png",
    },
    appleIcon120: {
      rel: "apple-touch-icon",
      sizes: "120x120",
      href: "/favicons/apple-icon-120x120.png",
    },
    appleIcon144: {
      rel: "apple-touch-icon",
      sizes: "144x144",
      href: "/favicons/apple-icon-144x144.png",
    },
    appleIcon152: {
      rel: "apple-touch-icon",
      sizes: "152x152",
      href: "/favicons/apple-icon-152x152.png",
    },
    appleIcon180: {
      rel: "apple-touch-icon",
      sizes: "180x180",
      href: "/favicons/apple-icon-180x180.png",
    },
    androidIcon: {
      rel: "icon",
      type: "image/png",
      sizes: "192x192",
      href: "/favicons/android-icon-192x192.png",
    },
    icon32: {
      rel: "icon",
      type: "image/png",
      sizes: "32x32",
      href: "/favicons/favicon-32x32.png",
    },
    icon96: {
      rel: "icon",
      type: "image/png",
      sizes: "96x96",
      href: "/favicons/favicon-96x96.png",
    },
    icon16: {
      rel: "icon",
      type: "image/png",
      sizes: "16x16",
      href: "/favicons/favicon-16x16.png",
    },
    manifest: { rel: "manifest", href: "/favicons/manifest.json" },
  },
  meta: {
    msapplicationTileColor: {
      name: "msapplication-TileColor",
      content: "#ffffff",
    },
    msapplicationTileImage: {
      name: "msapplication-TileImage",
      content: "/favicons/ms-icon-144x144.png",
    },
    themeColor: { name: "theme-color", content: "#ffffff" },
  },
});
</script>

<template>
  <div class="app-container">
    <RouterView></RouterView>
  </div>
</template>

<style>
html,
body,
#app {
  height: 100%;
  margin: 0;
}
</style>
