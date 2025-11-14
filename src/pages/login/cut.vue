<template>
  <div class="content-box">
    <div class="content">
      <div v-for="(message, index) in messages" :key="index" :class="[
        'message',
        message.role == 'user' ? 'user-message' : 'gpt-message',
        message.role == 'user' ? 'message-right' : 'message-left'
      ]">
        <div class="header" v-if="message.role == 'user'">
          <QuestionCircleTwoTone class="mr-10" />
          <h2 style="font-weight: 600;">{{ message.content }}</h2>
          {{ web_query }}
        </div>
        <div class="sources" v-if="message.role == 'user'">Sources</div>
        <div class="card-list">
          <a-card body-class="card-list-item" :bordered="false"
            v-for="(item, index) in message.search_results.slice(0, 3)" :key="index">
            <div class="cart-list-title">
              <a :href="item.link" target="_blank" class="title"
                style="text-decoration: none; color: inherit; cursor: pointer;">
                <h3><strong>{{ item.title }}</strong></h3>
              </a>
            </div>
            <div class="cart-list-text">{{ item.snippet }}</div>
          </a-card>
        </div>
        <div class="answer" v-if="message.role == 'gpt'">
          <a-card :body-style="{ padding: '20px' }">
            <template #title>
              <div class="answer-header" ref="scrollContainer">
                <BookTwoTone class="mr-10" />
                <h2>Answer</h2>
              </div>
            </template>
            <div class="messages" ref="messagesContainer">
              <div style="display: flex;">
                <div style="flex: 10;">
                  <template v-if="!message.content">
                    <div class="loading-container">
                      <a-space direction="vertical" align="center">
                        <a-spin size="large">
                          <template #indicator>
                            <LoadingOutlined style="font-size: 24px" spin />
                          </template>
                        </a-spin>
                        <div class="loading-text">
                          <a-typography-text>
                            <template v-if="loadingDots <= 1">Thinking</template>
                            <template v-else-if="loadingDots === 2">Thinking.</template>
                            <template v-else-if="loadingDots === 3">Thinking..</template>
                            <template v-else>Thinking...</template>
                          </a-typography-text>
                          <br />
                          <a-typography-text type="secondary" style="font-size: 14px;">
                            Please wait while I process your request
                          </a-typography-text>
                        </div>
                      </a-space>
                    </div>
                  </template>
                  <div v-else v-html="renderMarkdown(message.content)"></div>
                  <template v-if="message.content && message.streamComplete">
                    <br />
                    <div>
                      <h2>Related Questions</h2>
                      <a-divider />
                      <div style="cursor: pointer;" v-for="item in message.relatedQuestions" :key="item"
                        @click="RelatedhandleSubmit(item)" class="related-question-item">
                        <div class="title flex-between">
                          <span>{{ item }}</span>
                          <PlusOutlined class="plus-icon" />
                        </div>
                        <a-divider />
                      </div>
                    </div>
                  </template>
                </div>
                <div style="flex: 1;">
                  <a-tabs v-model:activeKey="message.activeName" tab-position="right" @tabClick="handleTabClick">
                    <a-tab-pane v-for="item in message.panes" :key="item.key" :tab="item.label">
                    </a-tab-pane>
                  </a-tabs>
                </div>
              </div>
            </div>
            <template #footer>
              <div class="answer-footer flex-between">
                <div class="answer-footer-left">
                  <div class="mr-20 flex-center">
                    <ShareAltOutlined class="mr-5" />Share
                  </div>
                  <div class="flex-center">
                    <RedoOutlined class="mr-5" />Rewrite
                  </div>
                </div>
                <div class="answer-footer-right">
                  <CopyOutlined class="mr-20" />
                  <EditOutlined class="mr-20" />
                  <MoreOutlined class="mr-20" />
                </div>
              </div>
            </template>
          </a-card>
        </div>
      </div>
      <div class="follow" @click="focusInput" ref="search">
        <div class="follow-box">
          <a-input-search size="large" :type="textarea" v-model:value="query" placeholder="Ask anything..."
            ref="inputField" allow-clear :bordered="false" @search="handleSubmit" enter-button>
          </a-input-search>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  SearchOutlined,
  ShareAltOutlined,
  RightOutlined,
  QuestionCircleTwoTone,
  BookTwoTone,
  PlusOutlined,
  RedoOutlined,
  CopyOutlined,
  EditOutlined,
  MoreOutlined,
  ArrowUpOutlined,
  LoadingOutlined,
} from "@ant-design/icons-vue";
import { registerUser } from "@/service/api/register/register";
import router from "@/router";
import { UserLogin } from "@/service/api/login_new/login";
import { createDialogue } from "@/service/api/Dialogue/Dialogue";
import { marked } from "marked";
import SearchResult from "./SearchResult.vue";
import { message } from "ant-design-vue";

export default {
  components: {
    SearchResult,
    ShareAltOutlined,
    RedoOutlined,
    CopyOutlined,
    EditOutlined,
    MoreOutlined,
    QuestionCircleTwoTone,
    BookTwoTone,
    SearchOutlined,
    PlusOutlined,
    RedoOutlined,
    CopyOutlined,
    EditOutlined,
    MoreOutlined,
    ArrowUpOutlined,
    LoadingOutlined,
  },
  data() {
    return {
      chat_response: "",
      query: "",
      userid: "",
      web_query: "",
      key: "",
      select: "",
      value1: "",
      messages: [],
      activeName: 1,
      results: [],
      msg: "",
      form: {
        username: "",
        password: "",
        msg: "",
      },
      confirmPassword: "",
      submitting: false,
      showLogin: false,
      search_self_results: {},
      message_id: "",
      isAnswered: true,
      isSearching: false,
      loadingDots: 1,
      loadingInterval: null,
    };
  },
  computed: {
    emailError() {
      if (!this.email) return "Email is required";
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.email)) return "Invalid email format";
      return "";
    },
    passwordError() {
      if (this.password !== this.confirmPassword)
        return "Passwords do not match";
      if (this.password.length < 8)
        return "Password must be at least 8 characters long";
      return "";
    },
  },

  mounted() {
    // 在组件挂载时检查 URL 参数并执行搜索
    const urlQuery = this.$route.query.query;
    if (urlQuery && !this.isSearching) {
      this.executeSearch(urlQuery);
    }
  },
  methods: {
    focusInput() {
      this.$refs.inputField.focus();
    },
    renderMarkdown(markdownText) {
      const safeMarkdownText = markdownText || "";
      try {
        const htmlContent = marked(safeMarkdownText);
        return htmlContent;
      } catch (error) {
        console.error("Error rendering Markdown:", error);
        return "";
      }
    },
    getSearchResults(messageId) {
      return this.searchResults[messageId] || [];
    },

    executeSearch(searchQuery) {
      // 状态检查
      if (!searchQuery || searchQuery.trim() === "") {
        message.warning("Please enter a query.");
        return;
      }

      if (this.isSearching || !this.isAnswered) {
        message.warning("Please wait for the current answer to complete.");
        return;
      }

      // 设置状态
      this.isSearching = true;
      this.isAnswered = false;

      try {
        // 检查用户登录
        this.userid = localStorage.getItem("userid");
        if (!this.userid) {
          message.warning("User not logged in. Please log in first.");
          this.isSearching = false;
          this.isAnswered = true;
          return;
        }

        // 添加消息
        this.addMessage(searchQuery, "user-message", [], []);
        this.addMessage("", "gpt-message", [], []);

        // 创建 EventSource
        const eventSource = createDialogue({
          query: searchQuery,
          userid: parseInt(this.userid),
          history_rounds: 3,
        });

        // 处理消息
        eventSource.onmessage = (event) => {
          if (event.data) {
            const response = JSON.parse(event.data);
            if (response.event === "END_OF_STREAM") {
              this.isSearching = false;
              this.isAnswered = true;
              const lastMessage = this.messages[this.messages.length - 1];
              if (lastMessage) {
                lastMessage.streamComplete = true;
              }
              eventSource.close();
              return;
            }
            this.updateMessage(
              response.gpt_content,
              "gpt-message",
              response.related_questions,
              response.raw_results
            );
          }
        };

        // 错误处理
        eventSource.onerror = (error) => {
          console.error("EventSource failed:", error);
          this.isSearching = false;
          this.isAnswered = true;
          message.error(
            "Error receiving data from server. Please try again later."
          );
          eventSource.close();
        };
      } catch (error) {
        console.error("Search execution error:", error);
        this.isSearching = false;
        this.isAnswered = true;
        message.error("An error occurred during search.");
      }
    },
    addMessage(text, role, relatedQuestions, search_results) {
      this.messages.push({
        content: text,
        role: role == "user-message" ? "user" : "gpt",
        relatedQuestions: relatedQuestions || [],
        activeName: "1",
        search_results: search_results || [],
        streamComplete: false,
        panes: [
          { key: "1", label: "Answer" },
          { key: "3", label: "Related Questions" },
        ],
      });
      // 确保 tabs 绑定了点击事件
      this.$nextTick(() => {
        const tabs = document.querySelector(".ant-tabs");
        if (tabs) {
          tabs.addEventListener("click", (e) => {
            if (e.target.textContent === "Related Questions") {
              this.handleTabClick("3");
            }
          });
        }
      });
    },
    updateMessage(content, role, relatedQuestions, search_results) {
      const lastMessage = this.messages[this.messages.length - 1];
      if (lastMessage) {
        lastMessage.content = content;
        lastMessage.relatedQuestions = (relatedQuestions || []).slice(0, 5); // 只取前五个相关问题
        lastMessage.search_results = search_results || [];
      }
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
            message.warning(response.data.message);
            return;
          } else {
            const token = response.data.token;
            localStorage.setItem("authToken", token);
            this.showLogin = false;
            message.success("Login successful.");
          }
        })
        .catch((error) => {
          console.error("Failed to register user:", error);
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
            message.warning(response.data.message);
          } else {
            message.success(response.data.message);
            router.push("/");
          }
        })
        .catch((error) => {
          console.error("Failed to register user:", error);
        });
    },
    handleSubmit() {
      this.executeSearch(this.query);
      this.query = ""; // 清空输入框
    },
    handlePaneClick(key) {
      console.log("Clicked on tab:", key);
      console.error("Clicked on tab:", key);
      if (key === "3") {
        const relatedQuestionsSection = this.$refs.relatedQuestionsSection;
        if (relatedQuestionsSection) {
          relatedQuestionsSection.scrollIntoView({ behavior: "smooth" });
          console.log("relatedQuestionsSection completed");
        }
        console.log("12341234relatedQuestionsSection completed");
      }
    },
    RelatedhandleSubmit(item) {
      if (!item || this.isSearching) {
        return;
      }

      if (!this.isAnswered) {
        message.warning("Please wait for the current answer to complete.");
        return;
      }

      this.executeSearch(item);
      this.query = ""; // 重置 query 以避免重复调用
      console.log("scrollToSearchBar called");
      // 获取搜索栏的 DOM 元素
      const searchBar = this.$refs.search;
      if (searchBar) {
        searchBar.scrollIntoView({ behavior: "smooth" });
        console.log("scrollToSearchBar completed");
      }
      // 滚动到页面底部
      this.$nextTick(() => {
        const bottomElement = document.documentElement;
        if (bottomElement) {
          bottomElement.scrollIntoView({ behavior: "smooth", block: "end" });
        }
      });
    },

    handleTabClick(tab) {
      console.log("Tab clicked:", tab);
      if (tab === "3") {
        this.$nextTick(() => {
          const relatedQuestionsSection = this.$refs.relatedQuestionsSection;
          if (relatedQuestionsSection) {
            relatedQuestionsSection.scrollIntoView({
              behavior: "smooth",
              block: "start",
            });
          } else {
            console.warn(
              "relatedQuestionsSection is not a DOM element or does not exist."
            );
          }
        });
      }
    },
    startLoadingAnimation() {
      this.loadingInterval = setInterval(() => {
        this.loadingDots = (this.loadingDots % 4) + 1;
      }, 500);
    },
    stopLoadingAnimation() {
      if (this.loadingInterval) {
        clearInterval(this.loadingInterval);
        this.loadingInterval = null;
      }
    },
  },
  watch: {
    messages: {
      handler(newMessages) {
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && !lastMessage.content) {
          this.startLoadingAnimation();
        } else {
          this.stopLoadingAnimation();
        }
      },
      deep: true,
    },
  },
  beforeUnmount() {
    this.stopLoadingAnimation();
  },
};
</script>

<style scoped lang="scss">
.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.flex-center {
  display: flex;
  align-items: center;
}

.mr-20 {
  margin-right: 20px;
}

.mr-10 {
  margin-right: 10px;
  font-size: 1.6em;
  margin-bottom: 10px;
  margin-left: 2px;
}

.mr-5 {
  margin-right: 5px;
}

.content-box {
  width: 100%;
  background: #f5f5f5;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: auto;

  .content {
    padding: 1.5rem;
    width: 100%;
    max-width: 1920px;
    margin: 0 auto;
    height: auto;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    overflow: visible;

    .header {
      display: flex;
      align-items: center;
      color: #1677ff;
      margin: 0.8rem 0 0.5rem 0;
      font-weight: 900;
      font-size: medium;
    }

    .sources {
      font-size: 2em;
      font-weight: bold;
      position: relative;
      margin: 0.5 rem 0;
    }

    .card-list {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      width: 100%;
      margin-bottom: 1rem;

      :deep(.ant-card) {
        width: 100%;
        height: 100%;
        margin: 0;
      }

      .cart-list-title {
        color: #333;
        margin-bottom: 0.25rem;
        h3 {
          margin: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }
      }

      .cart-list-text {
        color: #666;
        margin-top: 0.5rem;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
      }
    }

    .answer {
      width: 100%;
      margin: 0.75rem 0;

      :deep(.ant-card) {
        width: 100%;
        margin-right: 0;

        .ant-card-head {
          min-height: auto;
          padding: 0 16px;
        }

        .ant-card-head-title {
          padding: 12px 0;
        }
      }

      .answer-header {
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        height: auto;
        margin: 0;

        h3 {
          margin: 0;
          font-size: 16px;
          line-height: 1.5;
        }
      }

      .messages {
        margin-top: 8px;
      }

      :deep(.ant-card-body) {
        padding: 16px !important;
      }
    }

    :deep(.ant-card-head-title) {
      padding: 0;
    }

    :deep(.ant-card-body) {
      padding: 16px !important;
    }

    .answer-footer {
      color: #666;
      .answer-footer-left {
        display: flex;
        align-items: center;
      }
    }

    .follow {
      display: flex;
      justify-content: center;
      align-items: flex-start;
      padding: 0;
      margin: 1rem 0;
      cursor: pointer;

      .follow-box {
        width: 100%;
        background: #ffffff;
        max-width: 1600px;
        margin: 0 auto;
        border-radius: 5px;
        overflow: hidden;

        @media (min-width: 1920px) {
          max-width: 1800px;
        }

        :deep(.ant-input-group) {
          border-radius: 5px;
          overflow: hidden;
        }

        :deep(.ant-input-search) {
          .ant-input {
            border-radius: 5px 0 0 5px;
          }

          .ant-input-group-addon {
            .ant-btn {
              border-radius: 0 5px 5px 0;
            }
          }
        }

        .input-search {
          width: 100%;
          height: auto;
          background: #ffffff;
          border-radius: 5px;
        }
      }

      .follow-list {
        display: flex;
        flex-wrap: wrap;
        align-items: center;

        .follow-list-item {
          padding: 4px 8px;
          background: #e6f4ff;
          color: #1677ff;
          margin-right: 5px;
          border-radius: 5px;
          max-width: 280px;
          flex: 1;
          text-overflow: ellipsis;
          white-space: nowrap;
          overflow: hidden;

          &:last-child {
            margin-right: 0;
          }
        }
      }
    }
  }
}

/* 媒体查询优化 */
@media (max-width: 1920px) {
  .content-box .content {
    max-width: 1600px;
  }
}

@media (max-width: 1600px) {
  .content-box .content {
    max-width: 1200px;
  }
}

@media (max-width: 1200px) {
  .content-box .content {
    padding: 20px;
    max-width: 900px;
  }
}

@media (max-width: 900px) {
  .content-box .content {
    padding: 15px;

    .card-list {
      grid-template-columns: 1fr;
    }
  }
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  width: 100%;
  padding: 24px;
  text-align: center;

  .loading-text {
    margin-top: 16px;
    text-align: center;

    :deep(.ant-typography) {
      font-size: 18px;
      font-weight: 500;

      &.ant-typography-secondary {
        font-size: 14px;
        font-weight: normal;
      }
    }
  }
}

:deep(.anticon-loading) {
  font-size: 24px;
  color: #1890ff;
}

.related-question-item {
  transition: all 0.3s ease;

  .title {
    transition: all 0.3s ease;
    color: rgba(0, 0, 0, 0.85);

    .plus-icon {
      transition: all 0.3s ease;
      color: rgba(0, 0, 0, 0.45);
    }
  }

  &:hover {
    .title {
      color: var(--ant-primary-color, #1677ff);

      .plus-icon {
        color: var(--ant-primary-color, #1677ff);
      }
    }
  }
}
</style>