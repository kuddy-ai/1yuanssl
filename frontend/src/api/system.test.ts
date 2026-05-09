import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './client'
import { systemApi } from './system'

vi.mock('./client', () => ({
  default: {
    get: vi.fn(),
  },
}))

const mockedApiClient = vi.mocked(apiClient)

describe('systemApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads backend health status', async () => {
    const response = {
      status: 'healthy',
      service: '1yuanssl-backend',
      version: '0.1.0',
      database: 'healthy',
      mode: 'mvp',
    }
    mockedApiClient.get.mockResolvedValue(response)

    await expect(systemApi.getHealth()).resolves.toBe(response)

    expect(mockedApiClient.get).toHaveBeenCalledWith('/health')
  })
})
