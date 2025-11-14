<template>
  <div class="container">
    <a-typography>
      <a-typography-title>偏好设置</a-typography-title>
      <a-typography-paragraph>
        在这里，你可以通过提供个人信息、设定AI回答问题的规则以及选择首选回应语言，来自定义FinScope与你互动的方式。这些设置将帮助FinScope提供更加个性化、高效的体验，符合您的需求。
      </a-typography-paragraph>
    </a-typography>

    <a-tabs v-model:activeKey="activeTab">
      <a-tab-pane key="ai-profile" tab="AI Profile">
        <a-card class="preference-card" title="介绍自己">
          <a-textarea v-model:value="myself" :rows="4"
            placeholder="请简要描述你的工作、兴趣、背景等，这有助于AI更好地理解你。例如：我是一名Web开发者，主要使用JavaScript和Python，业余时间喜欢研究AI和打篮球。" />
        </a-card>

        <a-card class="preference-card" title="FinScope 回答规则">
          <a-textarea v-model:value="rules" :rows="4" placeholder="请详细说明你希望FinScope如何回答你的问题，例如回答方式的风格、技术深度、是否提供详细代码示例等。" />
        </a-card>

        <a-card class="preference-card" title="首选回应语言">
          <a-typography-paragraph>
            选择你希望AI使用的默认语言，这样可以让对话更符合你的日常习惯。
          </a-typography-paragraph>
          <a-select v-model:value="preferredLanguage" style="width: 200px" placeholder="请选择语言">
            <a-select-option v-for="item in languages" :key="item.value" :value="item.value">
              {{ item.label }}
            </a-select-option>
          </a-select>
        </a-card>

        <div class="button-container">
          <a-button type="primary" @click="handleSavePreferences" :loading="loading">
            保存偏好设置
          </a-button>
        </div>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { message } from "ant-design-vue";
import { getPreferences, savePreferences } from "@/service/api/clerk/clerk";

const activeTab = ref("ai-profile");
const myself = ref("");
const rules = ref("");
const preferredLanguage = ref("");
const loading = ref(false);
const userid = ref("");

const languages = [
  { value: "zh", label: "中文" },
  { value: "en", label: "English" },
];

onMounted(async () => {
  const storedUserId = localStorage.getItem("userid");
  if (storedUserId) {
    userid.value = storedUserId;
    await loadPreferences();
  } else {
    message.error("用户ID未找到");
  }
});

const loadPreferences = async () => {
  try {
    const response = await getPreferences(userid.value);
    if (response.code === 200) {
      myself.value = response.data.personal_info || "";
      rules.value = response.data.preset_prompts || "";
      preferredLanguage.value = response.data.language || "";
    }
  } catch (error) {
    console.error("加载偏好设置失败:", error);
    message.error("加载偏好设置失败");
  }
};

const handleSavePreferences = async () => {
  if (!myself.value.trim()) {
    message.warning("请填写个人介绍");
    return;
  }

  if (!rules.value.trim()) {
    message.warning("请填写回答规则");
    return;
  }

  if (!preferredLanguage.value) {
    message.warning("请选择首选语言");
    return;
  }

  loading.value = true;
  try {
    const data = {
      userid: userid.value,
      language: preferredLanguage.value,
      personal_info: myself.value.trim(),
      preset_prompts: rules.value.trim(),
    };

    const response = await savePreferences(data);
    if (response.code === 200) {
      message.success("偏好设置保存成功");
    } else {
      message.error(response.message || "偏好设置保存失败");
    }
  } catch (error) {
    console.error("保存偏好设置失败:", error);
    message.error("保存偏好设置失败");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 24px auto;
  padding: 0 24px;
}

.preference-card {
  margin-bottom: 24px;
}

.preference-card :deep(.ant-card-head) {
  border-bottom: none;
}

.button-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

:deep(.ant-tabs-nav) {
  margin-bottom: 24px;
}

:deep(.ant-card-body) {
  padding: 24px;
}

:deep(.ant-typography) {
  margin-bottom: 24px;
}

:deep(.ant-input) {
  resize: none;
}

:deep(.ant-card-head-title) {
  font-weight: 500;
  font-size: 16px;
}

:deep(.ant-typography-title) {
  margin-bottom: 16px !important;
}
</style>
