/**
 * 认证 API 函数
 */

import apiClient from './client'
import type { ApiResponse } from '../types/certificate'
import type { LoginRequest, LoginResponse } from '../types/auth'

export const authApi = {
  login: async (data: LoginRequest): Promise<ApiResponse<LoginResponse>> => {
    return apiClient.post('/auth/login', data)
  },
}
