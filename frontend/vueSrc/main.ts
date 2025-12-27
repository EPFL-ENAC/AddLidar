import { createApp } from "vue";

import { Quasar, Notify, Dialog, Meta } from "quasar";
import { createPinia } from "pinia";

// Import icon libraries
import "@quasar/extras/material-icons/material-icons.css";

// Import Roboto font
import "@quasar/extras/roboto-font/roboto-font.css";

// Import Quasar css
import "quasar/src/css/index.sass";

// Import Quasar flex addon for responsive spacing utilities
import "quasar/src/css/flex-addon.sass";
import "quasar/src/css/flex-addon.sass";

// Import app styles
import "@/assets/styles/app.scss";

import App from "@/App.vue";
import router from "@/router";

const pinia = createPinia();
const myApp = createApp(App);

myApp.use(pinia);
myApp.use(Quasar, {
  plugins: { Notify, Dialog, Meta },
});
myApp.use(router);

myApp.mount("#app");
