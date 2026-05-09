/**
 * 证书 API 函数
 */

import apiClient from './client'
import type {
  CertificateOrder,
  CertificateOrderCreate,
  AcmeChallenge,
  CertificateStats,
  ApiResponse,
} from '../types/certificate'

export const certificateApi = {
  /**
   * 创建证书订单
   */
  create: async (data: CertificateOrderCreate): Promise<ApiResponse<CertificateOrder>> => {
    return apiClient.post('/certificates/orders', data)
  },

  /**
   * 获取订单列表
   */
  list: async (params?: {
    status?: string
    limit?: number
    offset?: number
  }): Promise<ApiResponse<CertificateOrder[]>> => {
    return apiClient.get('/certificates/orders', { params })
  },

  /**
   * 获取订单详情
   */
  get: async (orderId: number): Promise<ApiResponse<CertificateOrder>> => {
    return apiClient.get(`/certificates/orders/${orderId}`)
  },

  /**
   * 获取订单的挑战信息
   */
  getChallenges: async (orderId: number): Promise<ApiResponse<AcmeChallenge[]>> => {
    return apiClient.get(`/certificates/orders/${orderId}/challenges`)
  },

  /**
   * 触发验证
   */
  validate: async (orderId: number): Promise<ApiResponse<CertificateOrder>> => {
    return apiClient.post(`/certificates/orders/${orderId}/validate`)
  },

  /**
   * 申请证书
   */
  issue: async (orderId: number): Promise<ApiResponse<CertificateOrder>> => {
    return apiClient.post(`/certificates/orders/${orderId}/issue`)
  },

  /**
   * 删除订单
   */
  delete: async (orderId: number): Promise<ApiResponse<null>> => {
    return apiClient.delete(`/certificates/orders/${orderId}`)
  },

  /**
   * 下载证书文件
   */
  download: async (orderId: number, fileType: 'fullchain' | 'privkey' | 'cert'): Promise<string> => {
    const response = await apiClient.get(`/certificates/orders/${orderId}/download/${fileType}`, {
      responseType: 'text',
    })
    return response as unknown as string
  },

  /**
   * 获取统计数据
   */
  getStats: async (): Promise<ApiResponse<CertificateStats>> => {
    return apiClient.get('/certificates/stats')
  },
}
