import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import Layout from "../layout/index.vue";
import { useUserStore } from '@/store/user'
import { message } from 'ant-design-vue';

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "home",
    component: Layout,
    redirect: "/login",
    children: [
      {
        path: "/login",
        name: "login",
        component: () => import(/* webpackChunkName: "page-login" */ "@/pages/login/Login.vue"),
        props: true // 启用 props
      },
      {
        path: "/clerk",
        name: "clerk",
        component: () => import(/* webpackChunkName: "page-clerk" */ "@/pages/login/clerk.vue"),
      },
      {
        path: "/register",
        name: "register",
        component: () => import(/* webpackChunkName: "page-register" */ "@/pages/register/register.vue"),
      },
      {
        path: "/cut",
        name: "LoginOld",
        component: () => import(/* webpackChunkName: "page-cut" */ "@/pages/login/cut.vue"),
        props: true // 启用 props
      },
      {
        path: "/history",
        name: "history",
        component: () => import(/* webpackChunkName: "page-history" */ "@/pages/index/HistoryPage.vue"),
      },
      {
        path: "/tutorial",
        name: "tutorial",
        component: () => import(/* webpackChunkName: "page-tutorial" */ "@/pages/index/TutorialPage.vue"),
      },
      {
        path: "/pricing",
        name: "pricing",
        component: () => import(/* webpackChunkName: "page-pricing" */ "@/pages/index/PricingPage.vue"),
      },
      {
        path: "/contact",
        name: "contact",
        component: () => import(/* webpackChunkName: "page-contact" */ "@/pages/index/ContactPage.vue"),
      },
      {
        path: "/preference",
        name: "preference",
        component: () => import(/* webpackChunkName: "page-preference" */ "@/pages/index/PreferencePage.vue"),
      },
      {
        path: "/paypal",
        name: "paypal",
        component: () => import(/* webpackChunkName: "page-paypal" */ "@/pages/pay/PayPal.vue"),
      },
      {
        path: "/stockAnalysis",
        name: "stockAnalysis",
        component: () => import(/* webpackChunkName: "page-stockAnalysis" */ "@/components/StockAnalysis.vue"),
      },
      {
        path: "/eventAnalysis",
        name: "eventAnalysis",
        component: () => import(/* webpackChunkName: "page-eventAnalysis" */ "@/components/EventAnalysis.vue"),
      }
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});



// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !userStore.isLoggedIn) {
    message.warning('321请先登录');
    next('/login');
  } else {
    next();
  }
});

export default router;
