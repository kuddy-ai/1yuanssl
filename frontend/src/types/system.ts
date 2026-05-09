/**
 * 系统状态相关类型定义
 */

export interface HealthStatus {
  status: string
  service: string
  version: string
  database: string
  mode: string
}
