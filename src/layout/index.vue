<template>
  <a-layout class="app">
    <Sider />
    <a-layout-content>
      <router-view></router-view>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { Layout, LayoutContent } from "ant-design-vue";
import Sider from "@/components/sider.vue";
</script>

<style scoped>
.app {
  min-height: 100vh;
  overflow: hidden;
}

:deep(.ant-layout-content) {
  height: 100vh;
  overflow-y: auto;
  padding: 20px;
}
</style>