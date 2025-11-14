import http from '@/service/http';
import { baseURL } from '@/service/baseurl';

console.log('VUE_APP_API_URL:', baseURL);

interface PreferencesData {
  userid: number;
  language: string;
  personal_info: string;
  preset_prompts: string[];
}

interface ResponseData<T> {
  code: number;
  data: T;
  msg?: string;
  err?: string;
}

// 保存用户偏好设置
export const saveUserPreferences = (data: PreferencesData) => {
  return http.post<ResponseData<void>>(baseURL + '/api/preferences', data)
    .then((response) => {
      return response.data;
    })
    .catch((error) => {
      // 提供更多上下文信息
      throw new Error(`Failed to save user preferences: ${error.message}`);
    });
};