<template>
  <a-card class="box-card">
    <template #title>
      <div class="card-header">
        <span>历史记录</span>
      </div>
    </template>
    <div class="scroll-container">
      <div v-for="(item, index) in historyList" :key="index" class="history-item">
        <div class="history-content">
          <div class="history-text">{{ item.text }}</div>
          <div class="history-time">{{ item.time }}</div>
        </div>
      </div>
    </div>
  </a-card>
</template>

<style scoped>
.scroll-container {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.history-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-text {
  flex: 1;
  margin-right: 20px;
}

.history-time {
  color: #999;
  font-size: 12px;
}
</style>
