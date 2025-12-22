import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "Home",
    component: () => import("@/views/HomeView.vue"),
  },
  {
    path: "/about",
    name: "About",
    component: () => import("@/views/AboutView.vue"),
  },
  {
    path: "/viewer/:missionId",
    name: "Viewer",
    component: () => import("@/views/ViewerView.vue"),
    props: true,
  },
  // Legacy redirect
  {
    path: "/mission/:id",
    redirect: (to) => ({ name: "Viewer", params: { missionId: to.params.id } }),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
