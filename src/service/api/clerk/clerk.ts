// src/service/api/clerk/clerk.ts
import request from '@/service/axios'
import { AxiosError } from 'axios'

interface ClerkLoginData {
  email: string
  clerk_id: string
  username?: string
}

interface ApiResponse {
  code: number
  message: string
  data?: any
}

export const loginWithClerk = async (data: ClerkLoginData): Promise<ApiResponse> => {
  try {
    const response = await request.post('/auth/login_my', data)
    return response.data
  } catch (error) {
    if ((error as AxiosError).response?.status === 400) {
      // 用户不存在,尝试注册
      const registerResponse = await request.post('/auth/register_my', data)
      if (registerResponse.data.code === 200) {
        // 注册成功,重新登录
        const loginResponse = await request.post('/auth/login_my', data)
        return loginResponse.data
      }
    }
    throw error
  }
}

export const getPreferences = async (userId: string): Promise<ApiResponse> => {
  try {
    const response = await request.get(`/api/preferences?userid=${userId}`)
    return response.data
  } catch (error) {
    if ((error as AxiosError).response?.status === 404) {
      return { code: 404, message: 'Preferences not found' }
    }
    throw error
  }
}

export const savePreferences = async (data: any): Promise<ApiResponse> => {
  const response = await request.post('/api/preferences', data)
  return response.data
}