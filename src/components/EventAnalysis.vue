<template>
  <div class="event-analysis-container">
    <a-typography-title :level="1">{{ eventDescription }}</a-typography-title>
    <a-card v-for="(section, index) in visibleSections" :key="index" class="analysis-card">
      <template #title>
        <a-typography-title :level="4">{{ section.title }}</a-typography-title>
      </template>
      <div class="card-content" :style="{ maxHeight: '400px', overflowY: 'auto' }">
        <template v-if="section.loading">
          <div class="loading-container">
            <a-space direction="vertical" align="center">
              <a-spin size="large">
                <template #indicator>
                  <LoadingOutlined style="font-size: 24px" spin />
                </template>
              </a-spin>
              <div class="loading-text">
                <a-typography-text>
                  <template v-if="loadingDots <= 1">Analyzing</template>
                  <template v-else-if="loadingDots === 2">Analyzing.</template>
                  <template v-else-if="loadingDots === 3">Analyzing..</template>
                  <template v-else>Analyzing...</template>
                </a-typography-text>
                <br />
                <a-typography-text type="secondary" style="font-size: 14px;">
                  Synthesizing market data to provide comprehensive insights...
                </a-typography-text>
              </div>
            </a-space>
          </div>
        </template>
        <template v-else>
          <div v-if="section.type === 'text'" v-html="renderMarkdown(section.content)"></div>
        
        <div v-else-if="section.type === 'stock-list'" class="stock-list">
          <div v-for="(stock, idx) in section.content" :key="idx" class="stock-item">
            <p class="stock-highlight" v-if="stock.highlight">{{ stock.highlight }}</p>
              <p><strong v-if="stock.name">{{ stock.name }}:</strong> 
                <span v-html="renderMarkdown(stock.description)"></span>
              </p>
            <div class="stock-chart" v-if="stock.chart">{{ stock.chart }}</div>
          </div>
        </div>
        
        <ul v-else-if="section.type === 'list'" class="content-list">
          <li v-for="(item, idx) in section.content" :key="idx">
            <strong v-if="item.title">{{ item.title }}</strong>
              <span v-html="renderMarkdown(item.description)"></span>
          </li>
        </ul>

        <div v-else-if="section.type === 'prospects'" class="prospects-list">
          <div v-for="(prospect, idx) in section.content" :key="idx" class="prospect-item">
            <h3>{{ prospect.title }}</h3>
              <div v-html="renderMarkdown(prospect.description)"></div>
            </div>
          </div>
        </template>
      </div>
      <template #actions>
        <div class="action-left">
          <a-button type="text">
            <template #icon><share-alt-outlined /></template>
            Share
          </a-button>
        </div>
        <div class="action-right">
          <a-space>
            <a-button type="text">
              <template #icon><copy-outlined /></template>
            </a-button>
            <a-button type="text">
              <template #icon><more-outlined /></template>
            </a-button>
          </a-space>
        </div>
      </template>
    </a-card>
  </div>
</template>

<script setup>
import { ShareAltOutlined, CopyOutlined, MoreOutlined, LoadingOutlined } from '@ant-design/icons-vue';
import { Card, Button, Space, Typography, Spin, message } from 'ant-design-vue';
import { ref, onMounted, watch, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { baseURL } from '@/service/baseurl';
import { marked } from 'marked';

const route = useRoute();
const loading = ref(false);
const eventDescription = ref('');
const description = ref('');
const sections = ref([
  {
    title: 'Market impact and investment hotspots',
    type: 'text',
    content: 'Analysis not available',
    loading: false
  },
  {
    title: 'Direct beneficiary stocks',
    type: 'stock-list',
    content: [{
      highlight: 'Market Performance',
      description: 'Analysis not available',
      chart: '[Stock Chart]'
    }],
    loading: false
  },
  {
    title: 'Potentially negatively affected stocks',
    type: 'stock-list',
    content: [{
      name: 'Affected Companies',
      description: 'Analysis not available',
      chart: '[Stock Chart]'
    }],
    loading: false
  },
  {
    title: 'Indirect beneficiaries of the industrial chain',
    type: 'list',
    content: [{
      title: 'Related Companies',
      description: 'Analysis not available'
    }],
    loading: false
  },
  {
    title: 'Potential risks and challenges',
    type: 'list',
    content: [{
      title: 'Risk Assessment',
      description: 'Analysis not available'
    }],
    loading: false
  },
  {
    title: 'Industry development prospects',
    type: 'prospects',
    content: [{
      title: 'Future Trends',
      description: 'Analysis not available'
    }],
    loading: false
  },
  {
    title: 'Opportunities for international investors',
    type: 'text',
    content: 'Analysis not available',
    loading: false
  },
  {
    title: 'Impact of policy changes on investments',
    type: 'list',
    content: [{
      title: 'Policy Impact',
      description: 'Analysis not available'
    }],
    loading: false
  },
  {
    title: 'Investment advice',
    type: 'prospects',
    content: [{
      title: 'Investment Strategy',
      description: 'Analysis not available'
    }],
    loading: false
  }
]);

// 初始化变量
let currentContext = ref('');
let currentAnswers = ref(new Map());
let searchResults = ref([]);

const loadingDots = ref(1);
const loadingInterval = ref(null);

const visibleSections = ref([]);
const completedSections = ref(new Set());

const fetchAnalysis = async () => {
  console.log("=== API Request Start ===");
  console.log("Base URL:", baseURL);
  
  // 重置状态
  visibleSections.value = [];
  completedSections.value.clear();
  currentContext.value = '';
  currentAnswers.value = new Map();
  searchResults.value = [];
  
  // 只显示并加载第一个section
  sections.value[0].loading = true;
  visibleSections.value.push(sections.value[0]);
  startLoadingAnimation();

  try {
    const desc = route.query.description;
    if (!desc) {
      throw new Error('No event description provided');
    }
    
    description.value = desc;
    eventDescription.value = desc;
    
    console.log("Request URL:", `${baseURL}/api/analyze-event`);
    console.log("Request payload:", { event_description: desc });

    // 发送 POST 请求并获取响应
    const response = await fetch(`${baseURL}/api/analyze-event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ event_description: desc })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = ''; // 添加缓冲区来处理分片数据

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // 保存未完成的行到缓冲区

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            console.log("Received SSE data:", data);
            
            // 清理 content 中的前缀和后缀，但保持空格
            if (data.content) {
              data.content = cleanContent(data.content);
            }
            
            switch (data.type) {
              case 'initial_context':
                sections.value[0].loading = true;
                currentContext.value = data.content; // 直接赋值，不是追加
                sections.value[0].content = currentContext.value;
                break;
                
              case 'answer':
              case 'complete':
                if (!currentAnswers.value.has(data.question_number)) {
                  currentAnswers.value.set(data.question_number, '');
                }
                const currentAnswer = currentAnswers.value.get(data.question_number);
                currentAnswers.value.set(
                  data.question_number,
                  currentAnswer ? `${currentAnswer} ${data.content}` : data.content
                );
                
                // 实时更新对应section的内容
                updateSectionContent(data.question_number, currentAnswers.value.get(data.question_number));
                break;
                
              case 'search_results':
                searchResults.value = data.content;
                // 实时更新搜索结果section
                if (searchResults.value && searchResults.value.length > 0) {
                  sections.value[3].content = searchResults.value.map(result => ({
                    title: result.title,
                    description: result.snippet
                  }));
                }
                break;
                
              case 'error':
                console.error("Received error from SSE:", data.content);
                message.error(data.content);
                break;
                
              case 'end':
                console.log("Stream completed");
                loading.value = false;
                break;
            }
          } catch (e) {
            console.error("Error parsing SSE data:", e);
          }
        }
      }
    }
  } catch (error) {
    console.log("=== API Error ===");
    console.log("Error:", error);
    message.error('Failed to fetch analysis data');
  } finally {
    stopLoadingAnimation();
  }
};

// 修改内容清理函数
const cleanContent = (content) => {
  if (!content) return '';
  
  // 保留原始空格和换行
  content = content.replace(/\s+/g, ' ').trim();
  
  // 移除 Answer 前缀但保留格式
  content = content.replace(/^(##\s*)?Answer\s*:\s*/i, '');
  
  // 移除 Related Questions 部分及其内容但保留格式
  const relatedQuestionsPattern = /(##\s*Related\s*Questions:?[\s\S]*?(?=##|$))/i;
  content = content.replace(relatedQuestionsPattern, '');
  
  // 移除数字列表格式的问题但保留格式
  content = content.replace(/\d+\s*\.\s*(?:What|How|In what|Which|Why).*?\?[\s\S]*?(?=\d+\s*\.|$)/g, '');
  
  // 处理markdown标签
  content = content.replace(/<sup>/g, '^').replace(/<\/sup>/g, '');
  
  return content.trim();
};

// 根据问题编号更新对应的section内容
const updateSectionContent = (questionNumber, content) => {
  const updateSection = (index, content, type = 'text') => {
    content = cleanContent(content);
    
    sections.value[index].loading = false;
    
    // 根据不同类型处理内容格式
    if (type === 'text') {
      sections.value[index].content = content;
    } else if (type === 'stock-list') {
      sections.value[index].content = [{
        highlight: '',
        description: content,
        chart: '[Stock Chart]'
      }];
    } else if (type === 'list') {
      // 处理列表格式
      const items = content.split('\n').filter(item => item.trim());
      sections.value[index].content = items.map(item => ({
        title: '',
        description: item
      }));
    } else if (type === 'prospects') {
      // 处理prospects格式
      sections.value[index].content = [{
        title: '',
        description: content
      }];
    }
    
    completedSections.value.add(index);
    if (!visibleSections.value.includes(sections.value[index])) {
      visibleSections.value.push(sections.value[index]);
    }
    
    const nextIndex = index + 1;
    if (nextIndex < sections.value.length && !visibleSections.value.includes(sections.value[nextIndex])) {
      sections.value[nextIndex].loading = true;
      visibleSections.value.push(sections.value[nextIndex]);
    }
  };

  // 更新问题编号和section的映射关系
  switch (questionNumber) {
    case "1": // Event Overview
      updateSection(0, content);
      break;
    case "2": // Direct Impact
      updateSection(1, content, 'stock-list');
      break;
    case "3": // Stakeholder Analysis
      updateSection(3, content, 'list'); // Indirect beneficiaries
      break;
    case "4": // Market Response
      updateSection(0, content);
      break;
    case "5": // Competitive Landscape
      updateSection(2, content, 'stock-list');
      break;
    case "6": // Regulatory Impact
      updateSection(7, content, 'list');
      break;
    case "7": // Economic Impact
      updateSection(6, content);
      break;
    case "8": // Technology & Innovation
      updateSection(5, content, 'prospects');
      break;
    case "9": // Risk Assessment
      updateSection(4, content, 'list');
      break;
    case "10": // Investment Opportunities
      updateSection(8, content, 'prospects'); // Investment advice
      break;
    case "11": // Future Outlook
      updateSection(5, content, 'prospects');
      break;
    case "12": // Strategic Recommendations
      updateSection(8, content, 'prospects');
      break;
  }
};

// 修改 renderMarkdown 函数
const renderMarkdown = (text) => {
  if (!text) return '';
  try {
    marked.setOptions({
      breaks: true,
      gfm: true,
      headerIds: true,
      mangle: false,
      smartLists: true,
      smartypants: true,
      xhtml: true,
      pedantic: false,
      sanitize: false
    });
    
    const cleanedText = cleanContent(text);
    
    // 处理特殊的markdown语法
    let renderedText = marked(cleanedText);
    
    // 保持空格和换行
    renderedText = renderedText.replace(/\n/g, '<br>');
    
    return renderedText;
  } catch (error) {
    console.error('Error rendering markdown:', error);
    return text;
  }
};

// 添加动画控制函数
const startLoadingAnimation = () => {
  loadingInterval.value = setInterval(() => {
    loadingDots.value = (loadingDots.value % 4) + 1;
  }, 500);
};

const stopLoadingAnimation = () => {
  if (loadingInterval.value) {
    clearInterval(loadingInterval.value);
    loadingInterval.value = null;
  }
};

onMounted(() => {
  fetchAnalysis();
});

//... existing code ...

// 在组件卸载时清理定时器
onUnmounted(() => {
  stopLoadingAnimation();
});
</script>

<style scoped>
.event-analysis-container {
  position: absolute;
  width: 1160px;
  left: 280px;
  top: -1px;
  display: flex;
  flex-direction: column;
  padding: 45px 48px;
  background: #F5F5F5;
}

:deep(.ant-typography) {
  font-size: 24px !important;
  margin-bottom: 24px !important;
}

:deep(.ant-card-head) .ant-typography {
  font-size: 16px !important;
  margin-bottom: 0 !important;
}

.analysis-card {
  margin-bottom: 24px !important;
}

.analysis-card:last-child {
  margin-bottom: 0 !important;
}

.main-content section {
  margin-bottom: 24px;
}

.main-content section:last-child {
  margin-bottom: 0;
}

.card-content {
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 16px;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* 自定义滚动条样式 */
.card-content::-webkit-scrollbar {
  width: 6px;
}

.card-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.card-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.card-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Markdown 样式 */
:deep(.markdown-content) {
  h1, h2, h3, h4, h5, h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
  }

  p {
    margin-bottom: 16px;
    line-height: 1.6;
  }

  ul, ol {
    margin-bottom: 16px;
    padding-left: 24px;
  }

  li {
    margin-bottom: 8px;
  }

  code {
    padding: 2px 4px;
    font-size: 90%;
    color: #c7254e;
    background-color: #f9f2f4;
    border-radius: 4px;
  }

  pre {
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    background-color: #f6f8fa;
    border-radius: 6px;
    margin-bottom: 16px;
  }

  blockquote {
    padding: 0 1em;
    color: #6a737d;
    border-left: 0.25em solid #dfe2e5;
    margin-bottom: 16px;
  }

  img {
    max-width: 100%;
    height: auto;
  }

  table {
    border-spacing: 0;
    border-collapse: collapse;
    margin-bottom: 16px;
    width: 100%;
  }

  td, th {
    padding: 6px 13px;
    border: 1px solid #dfe2e5;
  }

  tr:nth-child(2n) {
    background-color: #f6f8fa;
  }
}

/* 优化卡片内容间距 */
.stock-list, .content-list, .prospects-list {
  margin: 0;
  padding: 0;
}

.stock-item, .content-list li, .prospect-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.stock-item:last-child, .content-list li:last-child, .prospect-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.stock-list .stock-item {
  margin-bottom: 24px;
}

.stock-list .stock-item:last-child {
  margin-bottom: 0;
}

.stock-highlight {
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 8px;
}

.stock-chart {
  margin-top: 16px;
  color: #8c8c8c;
}

.content-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.content-list li {
  margin-bottom: 16px;
}

.content-list li:last-child {
  margin-bottom: 0;
}

.prospects-list .prospect-item {
  margin-bottom: 20px;
}

.prospects-list .prospect-item:last-child {
  margin-bottom: 0;
}

.prospects-list h3 {
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
  margin: 0 0 8px 0;
}

:deep(.ant-card) {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

:deep(.ant-card-head) {
  min-height: auto;
  padding: 0 24px;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.ant-card-head-title) {
  padding: 16px 0;
}

:deep(.ant-card-body) {
  padding: 24px;
}

:deep(.ant-card-actions) {
  display: flex;
  justify-content: space-between;
  padding: 0;
  border-top: 1px solid #f0f0f0;
  background: transparent;
  height: 40px;
  align-items: center;
}

:deep(.ant-card-actions) > li {
  margin: 0;
  padding: 0;
  width: 100% !important;
}

.action-left {
  display: flex;
  align-items: center;
  padding-left: 24px;
}

.action-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 24px;
  gap: 8px;
}

:deep(.ant-btn) {
  padding: 0 4px;
  height: 24px;
  line-height: 24px;
}

:deep(.ant-btn-text) {
  color: rgba(0, 0, 0, 0.45);
}

:deep(.ant-btn-text:hover) {
  color: #1890ff;
}

:deep(.anticon) {
  font-size: 14px;
}

@media (max-width: 1440px) {
  .event-analysis-container {
    position: relative;
    left: 0;
    width: 100%;
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .event-analysis-container {
    padding: 16px;
    gap: 16px;
  }
  
  :deep(.ant-card-body) {
    padding: 16px;
  }
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.loading-text {
  text-align: center;
  margin-top: 16px;
}

/* 确保内容不会溢出容器 */
:deep(.card-content) {
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  word-break: break-word !important;
  max-width: 100% !important;
}

:deep(.markdown-content), :deep(.card-content) {
  p, li, blockquote, pre, code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
  }
  
  ul, ol {
    padding-left: 2em;
    margin-bottom: 1em;
  }
  
  li {
    margin-bottom: 0.5em;
    list-style-position: outside;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1em;
    margin-bottom: 0.5em;
    font-weight: 600;
  }
}

/* 优化列表样式 */
.content-list {
  padding-left: 0;
  
  li {
    margin-bottom: 1em;
    padding-left: 1.5em;
    position: relative;
    
    &:before {
      content: "•";
      position: absolute;
      left: 0;
      color: #1890ff;
    }
  }
}

/* 优化内容格式 */
:deep(.card-content) {
  white-space: pre-wrap !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  word-break: break-word !important;
  
  p {
    margin-bottom: 1em;
    line-height: 1.6;
  }
  
  ul, ol {
    margin-left: 1.5em;
    margin-bottom: 1em;
  }
  
  li {
    margin-bottom: 0.5em;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 600;
  }
  
  blockquote {
    margin: 1em 0;
    padding-left: 1em;
    border-left: 4px solid #e8e8e8;
    color: rgba(0, 0, 0, 0.65);
  }
  
  code {
    background: #f5f5f5;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: monospace;
  }
  
  sup {
    vertical-align: super;
    font-size: smaller;
  }
}

/* 优化section内容间距 */
.stock-list, .content-list, .prospects-list {
  margin-top: 1em;
  
  .stock-item, li, .prospect-item {
    margin-bottom: 1.5em;
    padding-bottom: 1em;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      margin-bottom: 0;
      padding-bottom: 0;
      border-bottom: none;
    }
  }
  
  h3 {
    margin-bottom: 0.5em;
  }
}

/* 优化markdown渲染 */
:deep(.markdown-content) {
  line-height: 1.6;
  
  * + * {
    margin-top: 1em;
  }
  
  br {
    display: block;
    margin: 0.5em 0;
  }
}
</style>