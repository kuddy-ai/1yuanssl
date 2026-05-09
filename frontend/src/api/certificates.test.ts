import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './client'
import { certificateApi } from './certificates'
import { CertificateType, ChallengeType } from '../types/certificate'

vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockedApiClient = vi.mocked(apiClient)

describe('certificateApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates certificate orders with the submitted payload', async () => {
    const payload = {
      domains: ['example.com'],
      email: 'admin@example.com',
      cert_type: CertificateType.SINGLE,
      challenge_type: ChallengeType.HTTP_01,
      auto_renew: true,
    }
    const response = { success: true, data: { id: 1 } }
    mockedApiClient.post.mockResolvedValue(response)

    await expect(certificateApi.create(payload)).resolves.toBe(response)

    expect(mockedApiClient.post).toHaveBeenCalledWith('/certificates/orders', payload)
  })

  it('passes filters when listing certificate orders', async () => {
    const response = { success: true, data: [] }
    mockedApiClient.get.mockResolvedValue(response)

    await expect(certificateApi.list({ status: 'issued', limit: 10 })).resolves.toBe(response)

    expect(mockedApiClient.get).toHaveBeenCalledWith('/certificates/orders', {
      params: { status: 'issued', limit: 10 },
    })
  })

  it('requests PEM downloads as text and returns the response body', async () => {
    mockedApiClient.get.mockResolvedValue('pem-content')

    await expect(certificateApi.download(7, 'fullchain')).resolves.toBe('pem-content')

    expect(mockedApiClient.get).toHaveBeenCalledWith(
      '/certificates/orders/7/download/fullchain',
      { responseType: 'text' }
    )
  })
})
