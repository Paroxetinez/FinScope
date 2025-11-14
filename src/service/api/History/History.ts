import http from '@/service/http';
import { baseURL } from '@/service/baseurl';

console.log('VUE_APP_API_URL:', baseURL);

interface ConversationData {
  user_id: number;
}

interface ResponseData<T> {
  code: number;
  data: T;
  msg?: string;
  err?: string;
}

// 获取对话历史
export const fetchConversationHistory = (userid: number) => {
  const data: ConversationData = { user_id: userid };
  return http.post<ResponseData<void>>(baseURL + '/api/conversations', data)
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      // 提供更多上下文信息
      throw new Error(`Failed to fetch conversation history: ${error.message}`);
    });
};