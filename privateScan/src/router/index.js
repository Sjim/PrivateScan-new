
import PrivacyScan from "@/components/PrivacyScan";
import { createRouter, createWebHistory } from "vue-router";

const routerHistory = createWebHistory();

const routes = [
  //这里和vue2一样
  {
    path: "/",
    name: "HelloWorld",
    component: PrivacyScan,
  },
];

const router = createRouter({
  history: routerHistory,
  routes,
});

export default router;
