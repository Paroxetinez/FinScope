<template>
  <div class="main">
    <div class="image-container"><img src="@/assets/5.png" alt="" /></div>
    <div class="main-content">
      <div class="main-content-title">FinScope</div>
      <div class="main-content-text">Your Customized Financial AI Search</div>
      <a-input-search size="large" v-model:value="form.msg" placeholder="Ask anything..." :prefix-icon="SearchOutlined"
        enter-button clearable @search="Searchdata()">
      </a-input-search>
    </div>
    <div class="trending-section">
      <TrendingTopics />
    </div>
    <Sidebar v-if="isSidebarVisible" />
  </div>
</template>

<script>
import {
  SearchOutlined,
  RightOutlined,
  MessageOutlined,
} from "@ant-design/icons-vue";
import { registerUser } from "@/service/api/register/register";
import router from "@/router";
import { UserLogin } from "@/service/api/login_new/login";
import { createDialogue } from "@/service/api/Dialogue/Dialogue";
import SearchResult from "./SearchResult.vue";
import { message } from "ant-design-vue";
import TrendingTopics from "@/components/TrendingTopics.vue";
import Sider from "@/components/sider.vue";

export default {
  components: {
    SearchResult,
    createDialogue,
    SearchOutlined,
    RightOutlined,
    MessageOutlined,
    TrendingTopics,
    Sider,
  },
  data() {
    return {
      key: "",
      userid: "",
      select: "",
      value1: "",
      activeName: 1,
      results: [],
      chat_response: "",
      msg: "",
      form: {
        username: "",
        password: "",
        msg: "",
      },
      confirmPassword: "",
      submitting: false,
      showLogin: false,
      isSidebarVisible: true,
      siderCollapsed: false,
    };
  },
  watch: {
    siderCollapsed(newVal) {
      document.documentElement.style.setProperty('--sider-width', newVal ? '80px' : '200px');
    }
  },
  computed: {
    emailError() {
      if (!this.email) {
        return "Email is required";
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.email)) {
        return "Invalid email format";
      }
      return "";
    },
    passwordError() {
      if (this.password !== this.confirmPassword) {
        return "Passwords do not match";
      }
      if (this.password.length < 8) {
        return "Password must be at least 8 characters long";
      }
      return "";
    },
  },
  mounted() {
    this.checkUrlParamsForToken();
    // 设置初始侧边栏宽度
    document.documentElement.style.setProperty('--sider-width', this.siderCollapsed ? '80px' : '200px');
  },
  methods: {
    checkUrlParamsForToken() {
      // 获取 URL 参数
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get("token");
      // 检查 token 是否存在
      if (token) {
        // 存储 token 到 localStorage
        localStorage.setItem("authToken", token);
      }
    },
    Searchdata() {
      if (this.form.msg.trim() === "") {
        message.warning("Please enter a query.");
        return;
      }

      this.$router.push({ path: "/cut", query: { query: this.form.msg } });
      this.form.msg = ""; // 清空输入框
    },
    handleLogin() {
      if (!this.form.username) {
        message.warning("Please fill in your username.");
        return false;
      }
      if (!this.form.password) {
        message.warning("Please fill in your password.");
        return false;
      }
      UserLogin({
        username: this.form.username,
        password: this.form.password,
      })
        .then((response) => {
          if (response.data.code != 200) {
            message.error(response.data.message);
            return;
          } else {
            const token = response.data.token;
            const userid = response.data.user.id;
            localStorage.setItem("authToken", token);
            localStorage.setItem("userid", userid);
            this.showLogin = false;
            message.success("Login successful.");
          }
        })
        .catch((error) => {
          console.error("Failed to register user:", error);
          message.error("Login failed. Please try again.");
        });

      this.showLogin = false;
      this.form.username = "";
      this.form.password = "";
    },
    submitFormcom() {
      if (!this.form.username) {
        message.warning("Please fill in your username.");
        return false;
      }
      if (!this.email) {
        message.warning("Please fill in your email.");
        return false;
      }
      if (!this.form.password) {
        message.warning("Please fill in your password.");
        return false;
      }
      if (!this.confirmPassword) {
        message.warning("Please confirm your password.");
        return false;
      }
      registerUser({
        username: this.username,
        email: this.email,
        password: this.password,
      })
        .then((response) => {
          if (response.data.code != 200) {
            message.error(response.data.message);
          } else {
            message.success(response.data.message);
            router.push("/");
          }
        })
        .catch((error) => {
          console.error("Failed to register user:", error);
          message.error("Registration failed. Please try again.");
        });
    },
  },
};
</script>


<style lang="scss" scoped>
.mr-5 {
  margin-right: 5px;
}

.image-container {
  position: absolute;
  top: 20%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 60%;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none;
  user-select: none;
}

.image-container img {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
  opacity: 0.8;
  mix-blend-mode: multiply;
}

.main {
  display: flex;
  position: relative;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  padding: 10px;
  background-color: #f5f5f5;
}

.main-content {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 600px;
  text-align: center;
  padding: 20px;
  margin-bottom: 40px;
   margin-top: 140px;
}

.main-content-title {
  font-size: 2.5em;
  font-weight: bold;
  color: black;
  margin-bottom: 8px;
}

.main-content-text {
  font-size: 1.5em;
  color: rgba(0, 0, 0, 0.65);
  margin-bottom: 20px;
}

:deep(.ant-input-search) {
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
}

:deep(.ant-input-search .ant-input) {
  height: 50px;
  font-size: 16px;
}

:deep(.ant-input-search .ant-btn) {
  height: 50px;
  font-size: 16px;
}

.trending-section {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 1200px;
  margin-top: 20px;
  padding: 0 20px;
  margin-bottom: 10px;
}

@media (max-width: 768px) {
  .main-content-title {
    font-size: 2em;
  }

  .main-content-text {
    font-size: 1.2em;
  }

  .trending-section {
    padding: 0 10px;
  }
}
</style>