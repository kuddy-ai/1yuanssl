/**
 * 系统 API 函数
 */

import apiClient from './client'
import type { HealthStatus } from '../types/system'

export const systemApi = {
  /**
   * 获取后端健康状态
   */
  getHealth: async (): Promise<HealthStatus> => {
    return apiClient.get('/health')
  },
}
