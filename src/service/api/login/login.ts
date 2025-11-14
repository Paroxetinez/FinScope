//login.ts
import http from '@/service/http'
import * as T from './types'

export interface ILoginParams {
  userName: string
  passWord: string | number
}

const loginApi: T.ILoginApi = {
  login(params) {
    return http.post('/login', params)
  },
}

export default loginApi
