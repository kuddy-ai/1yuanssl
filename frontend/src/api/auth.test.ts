import { beforeEach, describe, expect, it, vi } from 'vitest'
import apiClient from './client'
import { authApi } from './auth'

vi.mock('./client', () => ({
  default: {
    post: vi.fn(),
  },
}))

const mockedApiClient = vi.mocked(apiClient)

describe('authApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('logs in with admin credentials', async () => {
    const payload = { username: 'admin', password: 'admin' }
    const response = {
      success: true,
      data: { access_token: 'dev-admin-token', token_type: 'bearer' as const },
    }
    mockedApiClient.post.mockResolvedValue(response)

    await expect(authApi.login(payload)).resolves.toBe(response)

    expect(mockedApiClient.post).toHaveBeenCalledWith('/auth/login', payload)
  })
})
