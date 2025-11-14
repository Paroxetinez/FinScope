<template>
  <a-layout-sider v-model:collapsed="collapsed" :trigger="null" collapsible :collapsedWidth="80" breakpoint="lg"
    @breakpoint="onBreakpoint" theme="light">
    <!-- 顶部区域 -->
    <meta name="google-site-verification" content="ZHR3raoUWtObzhuns-vvFpKZ-ab4E1CemyXB-HsuMZ4" />
    <div class="top-area">
      <a-space direction="vertical" :size="12">
        <div class="logo-container">
          <div class="logo" @click="goToHome">
            <img :src="collapsed ? logoSmall : logo6" :alt="collapsed ? 'small logo' : 'large logo'" class="logo-image"
              :class="{ 'logo-collapsed': collapsed }" />
          </div>
          <!-- 展开状态下的折叠按钮 -->
          <div v-if="!collapsed" class="collapse-button-expanded" @click="toggleCollapsed">
            <VerticalRightOutlined />
          </div>
        </div>

        <!-- 登录状态 -->
        <div v-if="isLoading">
          <a-spin />
        </div>
        <template v-else-if="!isSignedIn">
          <a-button type="primary" size="middle" block class="custom-button" @click="showSignInModal = true">
            <template v-if="!collapsed">Sign In</template>
            <UserOutlined v-else />
          </a-button>
        </template>
        <template v-if="isSignedIn">
          <div class="user-info">
            <a-space align="center">
              <UserButton afterSignOutUrl="/login" />
              <span v-if="!collapsed" class="username">{{ displayName }}</span>
            </a-space>
          </div>
        </template>
      </a-space>
    </div>

    <!-- 占位空间 -->
    <div class="flex-spacer"></div>

    <!-- 底部导航菜单 -->
    <a-menu mode="inline" class="nav-menu" :selectedKeys="[currentRoute]">
      <a-menu-item key="preference" @click="checkLoginAndNavigate('preference')">
        <template #icon>
          <EditOutlined />
        </template>
        Preference
      </a-menu-item>

      <a-menu-item key="history" @click="checkLoginAndNavigate('history')">
        <template #icon>
          <BarChartOutlined />
        </template>
        History
      </a-menu-item>

      <a-menu-item key="tutorial" @click="checkLoginAndNavigate('tutorial')">
        <template #icon>
          <FileTextOutlined />
        </template>
        Tutorial
      </a-menu-item>

      <a-menu-item key="pricing" @click="checkLoginAndNavigate('pricing')">
        <template #icon>
          <DollarOutlined />
        </template>
        Pricing
      </a-menu-item>

      <a-menu-item key="contact" @click="checkLoginAndNavigate('contact')">
        <template #icon>
          <MailOutlined />
        </template>
        Contact
      </a-menu-item>

      <a-menu-item v-if="isSignedIn" key="signout" @click="handleSignOut" danger>
        <template #icon>
          <LogoutOutlined />
        </template>
        Exit
      </a-menu-item>

      <!-- 只在折叠状态下显示底部折叠按钮 -->
      <a-menu-item v-if="collapsed" class="collapse-trigger" @click="toggleCollapsed">
        <template #icon>
          <VerticalLeftOutlined />
        </template>
        Expand
      </a-menu-item>
    </a-menu>

    <!-- 将 SignIn 移到 template 最外层,确保它在整个页面居中 -->
    <div v-if="showSignInModal" class="clerk-modal-wrapper" @click.self="showSignInModal = false">
      <SignIn @close="showSignInModal = false" />
    </div>
  </a-layout-sider>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { SignIn, UserButton, useUser, useClerk, useAuth } from "vue-clerk";
import { useRouter, useRoute } from "vue-router";
import { useUserStore } from "@/store/user";
import { storeToRefs } from "pinia";
import { message } from "ant-design-vue";
import request from "@/service/axios"; // 修改这里,使用自定义的 axios 实例
import { loginWithClerk } from "@/service/api/clerk/clerk";
import {
  UserOutlined,
  EditOutlined,
  BarChartOutlined,
  FileTextOutlined,
  DollarOutlined,
  MailOutlined,
  LogoutOutlined,
  VerticalRightOutlined,
  VerticalLeftOutlined,
} from "@ant-design/icons-vue";

// 导入图片
import logo6 from "@/assets/6.png";
import logoSmall from "@/assets/logo.png";

const router = useRouter();
const route = useRoute();
const { user } = useUser();
const { isSignedIn } = useAuth();
const { signOut } = useClerk();
const userStore = useUserStore();
const { isLoggedIn, userInfo } = storeToRefs(userStore);
const isLoading = ref(true);
const collapsed = ref(false);
const isMobile = ref(false);
const showSignInModal = ref(false);

// 计算属性:显示名称
const displayName = computed(() => {
  if (user.value) {
    return (
      user.value.username ||
      user.value.firstName ||
      user.value.emailAddresses[0].emailAddress
    );
  }
  return "";
});

// 删除重复的 watch,保留一个完整的处理逻辑
watch(isSignedIn, async (newValue) => {
  console.log("Clerk isSignedIn changed:", newValue);
  if (newValue && user.value) {
    try {
      isLoading.value = true;

      // 尝试登录
      const loginResponse = await request.post("/auth/login_my", {
        email: user.value.emailAddresses[0].emailAddress,
        clerk_id: user.value.id,
        username: user.value.username || user.value.firstName,
      });

      if (loginResponse.data.code === 200) {
        const { user: userData, token } = loginResponse.data;
        userStore.setUserInfo({
          id: userData.id,
          username: userData.username,
          email: userData.email,
        });
        userStore.setToken(token);
        localStorage.setItem("userid", userData.id.toString());

        message.success("Login Success");
      } else if (loginResponse.data.code === 400) {
        // 用户不存在,尝试注册
        console.log("User not found, attempting registration");
        const registerResponse = await request.post("/auth/register_my", {
          email: user.value.emailAddresses[0].emailAddress,
          clerk_id: user.value.id,
          username: user.value.username || user.value.firstName,
        });

        if (registerResponse.data.code === 200) {
          // 注册成功,再次尝试登录
          const secondLoginResponse = await request.post("/auth/login_my", {
            email: user.value.emailAddresses[0].emailAddress,
            clerk_id: user.value.id,
          });

          if (secondLoginResponse.data.code === 200) {
            const { user: newUserData, token } = secondLoginResponse.data;
            userStore.setUserInfo({
              id: newUserData.id,
              username: newUserData.username,
              email: newUserData.email,
            });
            userStore.setToken(token);
            localStorage.setItem("userid", newUserData.id.toString());

            message.success("Register and Login Success");
            router.push("/login");
          } else {
            throw new Error("Second login attempt failed after registration");
          }
        } else {
          throw new Error("Registration failed");
        }
      } else {
        throw new Error(`Unexpected response code: ${loginResponse.data.code}`);
      }
    } catch (error) {
      console.error("Login/Registration process failed:", error);
      message.error(error.message || "登录失败,请重试");
    } finally {
      isLoading.value = false;
    }
  } else {
    // 如果用户未登录，也要设置 isLoading 为 false
    isLoading.value = false;
  }
});

// 简化 handleSignIn 函数
const handleSignIn = async () => {
  try {
    isLoading.value = true;
    // Clerk 登录处理已经在 watch 中完成
  } catch (error) {
    console.error("Sign in process failed:", error);
    message.error("登录过程出错,请重试");
  } finally {
    isLoading.value = false;
  }
};

// 删除重复的 onMounted，合并为一个
onMounted(async () => {
  try {
    await userStore.initUserState();
    // 检查初始登录状态
    if (!isSignedIn.value) {
      isLoading.value = false;
    }
  } catch (error) {
    console.error("Failed to initialize:", error);
    isLoading.value = false;
  }
});

const toggleCollapsed = () => {
  collapsed.value = !collapsed.value;
};
const onBreakpoint = (broken) => {
  isMobile.value = broken;
  collapsed.value = broken;
};

// 当前路由
const currentRoute = computed(() => route.name);

// 退出登录
const handleSignOut = async () => {
  try {
    await signOut();
    userStore.clearUserInfo();
    message.success("退出成功");
    router.push("/login");
  } catch (err) {
    console.error("Error signing out:", err);
    message.error("退出失败,请重试");
  }
};

// 添加登录检查和导航函数
const checkLoginAndNavigate = (route) => {
  if (!isSignedIn.value) {
    message.warning("Please sign in first");
    showSignInModal.value = true;
    return;
  }

  // 根据路由进行导航
  switch (route) {
    case "preference":
      router.push("/preference");
      break;
    case "history":
      router.push("/history");
      break;
    case "tutorial":
      router.push("/tutorial");
      break;
    case "pricing":
      router.push("/paypal");
      break;
    case "contact":
      router.push("/contact");
      break;
  }
};

// 其他方法
const goToHome = () => router.push("/");
</script>

<style scoped>
/* 原有样式保持不变,添加响应样式 */
@media screen and (max-width: 992px) {
  :deep(.ant-layout-sider) {
    position: fixed;
    z-index: 999;
    height: 100vh;
    left: 0;
    top: 0;
  }
}
/* 添加登录弹窗相关样式 */
:deep(.login-modal) {
  display: flex;
  align-items: center;
  justify-content: center;
}
:deep(.ant-modal-content) {
  padding: 0;
  border-radius: 8px;
  overflow: hidden;
}
:deep(.ant-modal-body) {
  padding: 0;
}
.clerk-container {
  width: 100%;
  min-height: 400px; /* 根据实际内容调整 */
  display: flex;
  align-items: center;
  justify-content: center;
}
/* 确保弹窗在最上层 */
:deep(.ant-modal-wrap) {
  z-index: 1000;
}
/* 定义按钮样式保持不变 */
:deep(.custom-button) {
  height: 32px;
  padding: 0 15px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  background: #1677ff;
  border: 1px solid #1677ff;
  box-shadow: 0px 2px 0px rgba(5, 145, 255, 0.1);
  border-radius: 6px;
  width: 240px;
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
}

:deep(.custom-button:hover) {
  background: #4096ff;
  border-color: #4096ff;
}

:deep(.ant-layout-sider-collapsed .company-text),
:deep(.ant-layout-sider-collapsed .username) {
  display: none;
}

:deep(.ant-layout-sider-collapsed .custom-button) {
  width: 48px !important;
  padding: 0;
}

.collapse-trigger {
  position: absolute;
  bottom: 24px;
  right: 16px;
  cursor: pointer;
  font-size: 16px;
  color: rgba(0, 0, 0, 0.65);
  transition: color 0.3s;
}

.collapse-trigger:hover {
  color: #1890ff;
}
:deep(.custom-button) {
  height: 32px;
  width: 100% !important; /* 使用100%宽度自适应父容器 */
  max-width: 200px; /* 最大宽度限制 */
  padding: 0 15px;
  display: flex;
  background: #1677ff;
  border: 1px solid #1677ff;
  box-shadow: 0px 2px 0px rgba(5, 145, 255, 0.1);
  border-radius: 6px;
  transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
}

/* 折叠状态样式 */
:deep(.ant-layout-sider-collapsed .custom-button) {
  width: 48px !important;
  min-width: 240px;
  padding: 0 8px;
}
/* 确保按钮容器也能自适应 */
.top-area {
  padding: 16px 16px;
  width: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.custom-button:hover) {
  background: #4096ff;
  border-color: #4096ff;
}
:deep(.ant-layout-sider-children) {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.top-area {
  padding: 16px 16px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 0;
}

.logo-circle {
  width: 40px;
  height: 40px;
  border: 8px solid #1890ff; /* 空心圆圈 */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.company-text {
  font-size: 20px;
  font-weight: 600;
  color: #000000;
}

.user-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0px 4px;
  gap: 4px;
  width: 280px;
  height: 40px;
  background: #ffffff;
}

:deep(.ant-card-body) {
  padding: 5px;
  width: 100%;
}

.username {
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.88);
}

.flex-spacer {
  flex: 1;
}

.nav-menu {
  border-right: none;
  margin-top: auto;
}

:deep(.ant-menu-item) {
  height: 50px;
  line-height: 50px;
  font-size: 16px;
}

.logo-image {
  width: 130px;
  height: auto;
  object-fit: contain;
  transition: all 0.3s;
}

.logo-image.logo-collapsed {
  width: 40px;
  height: 40px;
}

/* UserButton 自定义样式 */
:deep(.cl-userButtonBox) {
  height: 40px !important;
  width: 40px !important;
}

:deep(.cl-userButtonTrigger) {
  height: 100% !important;
  width: 100% !important;
}

:deep(.cl-userButtonAvatarBox) {
  width: 100% !important;
  height: 100% !important;
}

:deep(.cl-userButtonAvatarImage) {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
}

/* 添加居中显示的样式 */
.clerk-modal-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  cursor: pointer;
}

.clerk-modal-wrapper :deep(.cl-card) {
  cursor: default;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.username {
  font-size: 16px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.88);
  margin-left: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

/* 添加 tab 的鼠标指针样式 */
:deep(.ant-tabs-tab) {
  cursor: pointer;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  position: relative;
  padding: 8px 16px 8px 0; /* 增加右侧内边距 */
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.logo-image {
  width: 130px;
  height: auto;
  object-fit: contain;
  transition: all 0.3s;
}

.logo-image.logo-collapsed {
  width: 40px;
  height: 40px;
}

.collapse-button-expanded {
  cursor: pointer;
  font-size: 16px;
  color: rgba(0, 0, 0, 0.65);
  padding: 8px;
  margin-left: 24px; /* 增加左侧间距 */
  transition: color 0.3s;
  display: flex;
  align-items: center;
}

.collapse-button-expanded:hover {
  color: #1890ff;
}

.collapse-trigger {
  position: absolute;
  bottom: 24px;
  right: 16px;
  cursor: pointer;
  font-size: 16px;
  color: rgba(0, 0, 0, 0.65);
  transition: color 0.3s;
  display: none;
}

:deep(.ant-layout-sider-collapsed) .collapse-trigger {
  display: block;
}

:deep(.ant-layout-sider-collapsed) .collapse-button-expanded {
  display: none;
}
</style>