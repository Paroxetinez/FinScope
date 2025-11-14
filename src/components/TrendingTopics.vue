<template>
  <div class="trending-topics">
    <div class="trending-header">
      <div class="trending-title">
        <LineChartOutlined />
        <span>Trending Topics</span>
      </div>
    </div>
    <div class="topics-container">
      <div v-for="(topic, index) in topics" :key="index" class="topic-item" @click="handleTopicClick(topic)">
        <div class="topic-number">{{ String(index + 1).padStart(2, '0') }}</div>
        <div class="topic-content">{{ topic.content }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { LineChartOutlined } from '@ant-design/icons-vue';

const router = useRouter();

const topics = ref([
  {
    content: "The U.S. Supreme Court upheld TikTok's injunction, and TikTok is at risk of shutting down"
  },
  {
    content: "Chinese President Xi Jinping spoke by phone with US President-elect Donald Trump at the request"
  },
  {
    content: "American netizens said that stereotypes about China have been shattered"
  },
  {
    content: "The TikTok ban may have led to an influx of users into RedNote"
  },
  {
    content: "CES 2025 takes place in Las Vegas, USA and AI is the biggest topic at CES"
  },
  {
    content: "Nvidia's chief executive, Jensen Huang, plans to visit several major cities in China"
  }
]);

const handleTopicClick = (topic) => {
  router.push({
    path: '/eventAnalysis',
    query: { description: topic.content }
  });
};
</script>

<style scoped>
.trending-topics {
  width: 100%;
  max-width: 932px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0;
  gap: 16px;
  background: transparent;
}

.trending-header {
  width: 100%;
  display: flex;
  align-items: center;
}

.trending-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1677ff;
  font-size: 20px;
  font-weight: 600;
}

.trending-title :deep(.anticon) {
  font-size: 20px;
}

.topics-container {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px 32px;
  overflow: hidden;
}

.topic-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 40px;
  max-height: 72px;
  overflow: hidden;
  padding: 0;
}

.topic-item:hover {
  opacity: 0.8;
}

.topic-number {
  font-size: 20px;
  color: #999;
  font-weight: 500;
  min-width: 28px;
}

.topic-content {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.88);
  line-height: 1.5;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  font-weight: 500;
  margin: 0;
}

@media (max-width: 1200px) {
  .trending-topics {
    max-width: 90%;
  }

  .topics-container {
    gap: 20px 24px;
  }
}

@media (max-width: 992px) {
  .topics-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px 20px;
  }
}

@media (max-width: 768px) {
  .trending-topics {
    padding: 0 16px;
  }

  .topics-container {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style> 