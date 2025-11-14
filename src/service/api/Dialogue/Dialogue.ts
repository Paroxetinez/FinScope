// api.ts
import http from '@/service/http';
import { baseURL } from '@/service/baseurl';

console.log('VUE_APP_API_URL:', baseURL);

interface RegisterData {
  query: String;
  userid: number;
  history_rounds: number;
}

interface LoginData {
  username: string;
  password: string;
}

interface ResponseData<T> {
  code: number;
  data: T;
  msg?: string;
  err?: string;
}

// 会话函数
export const createDialogue = (data: RegisterData) => {
  const url = new URL('/api/chat', baseURL); // 确保baseURL没有结尾的斜杠
  url.searchParams.append('query', String(data.query)); // 强制转换为字符串
  url.searchParams.append('userid', String(data.userid));
  url.searchParams.append('history_rounds', String(data.history_rounds));
  console.log('Generated URL:', url.toString()); // 打印生成的URL,确保其正确

  const eventSource = new EventSource(url.toString());

  eventSource.onopen = () => {
    console.log("EventSource connection opened.");
  };

  eventSource.addEventListener('close', () => {
    console.log("EventSource connection closed.");
  });

  return eventSource;
};
