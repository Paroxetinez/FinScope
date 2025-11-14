import axios, { AxiosRequestConfig, AxiosResponse } from 'axios'
import NProgress from 'nprogress'
import { message } from 'ant-design-vue'

// 设置请求头和请求路径
axios.defaults.baseURL = '/'
axios.defaults.timeout = 20000
axios.defaults.headers.post['Content-Type'] = 'application/json;charset=UTF-8'

// 请求拦截器
axios.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const token = localStorage.getItem('authToken')
    if (!token) {
      // 如果没有 authToken，则提示用户登录
      message.warning('Please log in.')
      return Promise.reject(new Error('Not logged in'))
    }
    // 类型断言告诉 TypeScript 这是一个字符串对象
    (config.headers as Record<string, string>)['X-Token'] = token
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axios.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data } = response

    if (data.code === 200) {
      return data
    } else if (data.code === 401) {
      // 处理403状态码的情况，提示重新登录
      message.error('Session expired or unauthorized access. Please log in again.')
      localStorage.removeItem('authToken') // 清除本地存储的 token
      return Promise.reject(data)
    } else {
      // 处理非200状态码的情况
      message.error(data.msg || 'Server returned an error: ' + response.status)
      return Promise.reject(data)
    }
  },
  (error: any) => {
    message.error(error.message || 'Request failed')
    return Promise.reject(error)
  }
)

interface ResType<T> {
  code: number
  data?: T
  msg: string
  err?: string
}

interface Http {
  get<T>(url: string, params?: unknown): Promise<ResType<T>>
  post<T>(url: string, params?: unknown): Promise<ResType<T>>
  upload<T>(url: string, params: unknown): Promise<ResType<T>>
  download(url: string): void
}

const http: Http = {
  get(url, params) {
    return new Promise((resolve, reject) => {
      NProgress.start()
      axios
        .get(url, { params })
        .then((res) => {
          NProgress.done()
          resolve(res.data)
        })
        .catch((err) => {
          NProgress.done()
          reject(err)
        })
    })
  },
  post(url, params) {
    return new Promise((resolve, reject) => {
      NProgress.start()
      axios
        .post(url, params)
        .then((res) => {
          NProgress.done()
          resolve(res.data)
        })
        .catch((err) => {
          NProgress.done()
          reject(err)
        })
    })
  },
  upload(url, file) {
    return new Promise((resolve, reject) => {
      NProgress.start()
      axios
        .post(url, file, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        .then((res) => {
          NProgress.done()
          resolve(res.data)
        })
        .catch((err) => {
          NProgress.done()
          reject(err)
        })
    })
  },
  download(url) {
    const iframe = document.createElement('iframe')
    iframe.style.display = 'none'
    iframe.src = url
    iframe.onload = function () {
      document.body.removeChild(iframe)
    }
    document.body.appendChild(iframe)
  },
}

export default http