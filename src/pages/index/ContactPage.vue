<template>
  <div class="preference-container">
    <h1>偏好设置</h1>
    <div class="preference-content">
      <div class="preference-item">
        <label>主题颜色：</label>
        <a-input v-model:value="theme" placeholder="请输入主题颜色" />
      </div>
      <div class="preference-item">
        <label>字体大小：</label>
        <a-input v-model:value="fontSize" placeholder="请输入字体大小" />
      </div>
      <div class="preference-item">
        <label>语言：</label>
        <a-input v-model:value="language" placeholder="请输入语言" />
      </div>
      <div class="preference-item">
        <label>通知设置：</label>
        <a-input v-model:value="notification" placeholder="请输入通知设置" />
      </div>
      <div class="preference-actions">
        <a-button type="primary" @click="savePreferences">保存偏好设置</a-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.preference-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.preference-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.preference-item {
  margin-bottom: 20px;
}

.preference-item label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
}

.preference-actions {
  text-align: center;
  margin-top: 30px;
}

:deep(.ant-input) {
  width: 100%;
}
</style>