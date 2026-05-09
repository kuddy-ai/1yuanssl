/**
 * 证书相关类型定义
 */

export enum CertificateType {
  SINGLE = 'single',
  WILDCARD = 'wildcard',
  MULTI = 'multi'
}

export enum ChallengeType {
  HTTP_01 = 'http-01',
  DNS_01 = 'dns-01'
}

export enum OrderStatus {
  PENDING = 'pending',
  VALIDATING = 'validating',
  ISSUED = 'issued',
  FAILED = 'failed',
  EXPIRED = 'expired',
  RENEWING = 'renewing'
}

export interface CertificateOrder {
  id: number
  domains: string[]
  email: string
  cert_type: CertificateType
  challenge_type: ChallengeType
  status: OrderStatus
  auto_renew: boolean
  acme_order_url?: string
  not_before?: string
  not_after?: string
  error_message?: string
  created_at: string
  updated_at: string
  days_until_expiry?: number
  is_expired: boolean
}

export interface CertificateOrderCreate {
  domains: string[]
  email: string
  cert_type: CertificateType
  challenge_type: ChallengeType
  auto_renew: boolean
}

export interface AcmeChallenge {
  id: number
  order_id: number
  domain: string
  challenge_type: string
  status: 'pending' | 'valid' | 'invalid'
  token?: string
  key_authorization?: string
  dns_txt_name?: string
  dns_txt_value?: string
  validated_at?: string
  created_at: string
}

export interface CertificateStats {
  total: number
  issued: number
  failed: number
  expiring: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}