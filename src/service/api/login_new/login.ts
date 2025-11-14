// api.ts
import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { baseURL } from '@/service/baseurl'; // Import the registerUser function



const instance = axios.create({
  baseURL: baseURL,
  timeout: 5000
});

interface RegisterData {
  username: string;
  email: string;
  password: string;
  msg: string
}


export const UserLogin = (data: RegisterData) => {
  return instance.post<{}, AxiosResponse<void, RegisterData>>('/auth/login_my', data)
    .then((response) => {
      return response;
    })
    .catch((error: AxiosError) => {
      throw new Error(`Failed to register user: ${error.message}`);
    });
};

