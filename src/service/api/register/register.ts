// api.ts
import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { baseURL } from '@/service/baseurl'; // Import the registerUser function



console.log('VUE_APP_API_URL:', baseURL);
const instance = axios.create({
  baseURL: baseURL,
  timeout: 20000
});

interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export const registerUser = (data: RegisterData) => {
  return instance.post<{}, AxiosResponse<void, RegisterData>>('/auth/register_my', data)
    .then((response) => {
      return response;
    })
    .catch((error: AxiosError) => {
      throw new Error(`Failed to register user: ${error.message}`);
    });
};