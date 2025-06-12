import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue"; // if using Vue; install with npm install --save-dev @vitejs/plugin-vue
import path from "path";
import { quasar, transformAssetUrls } from "@quasar/vite-plugin";
import { fileURLToPath } from "node:url";

export default defineConfig({
  // adjust root if needed (e.g., to "src" or another folder)
  root: "./vueSrc/",
  publicDir: "public",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "vueSrc"),
    },
  },
  build: {
    outDir: "dist",
    // other build options as required
  },
  plugins: [
    vue({
      template: { transformAssetUrls },
    }),

    // @quasar/plugin-vite options list:
    // https://github.com/quasarframework/quasar/blob/dev/vite-plugin/index.d.ts
    quasar({
      sassVariables: fileURLToPath(
        new URL("./vueSrc/quasar-variables.sass", import.meta.url),
      ),
    }),
  ],
  server: {
    proxy: {
      "/api": {
        target: "http://0.0.0.0:8000/",
        changeOrigin: true,
        secure: false,
        ws: true,
        rewriteWsOrigin: true,
      },
      "/static": {
        target: "https://addlidar-potree-dev.epfl.ch",
        changeOrigin: true,
        secure: false,
        ws: true,
        rewriteWsOrigin: true,
      },
    },
  },
});
