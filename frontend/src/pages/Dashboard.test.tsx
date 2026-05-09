import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import Dashboard from './Dashboard'
import { certificateApi } from '../api/certificates'
import { CertificateType, ChallengeType, OrderStatus } from '../types/certificate'
import type { CertificateOrder } from '../types/certificate'

vi.mock('../api/certificates', () => ({
  certificateApi: {
    getStats: vi.fn(),
    list: vi.fn(),
  },
}))

const mockOrder: CertificateOrder = {
  id: 12,
  domains: ['example.com', 'www.example.com'],
  email: 'admin@example.com',
  cert_type: CertificateType.MULTI,
  challenge_type: ChallengeType.HTTP_01,
  status: OrderStatus.ISSUED,
  auto_renew: true,
  created_at: '2026-01-02T03:04:05Z',
  updated_at: '2026-01-02T03:04:05Z',
  not_after: '2026-04-02T03:04:05Z',
  is_expired: false,
}

describe('Dashboard', () => {
  it('loads certificate stats and recent orders', async () => {
    vi.mocked(certificateApi.getStats).mockResolvedValue({
      success: true,
      data: { total: 3, issued: 2, failed: 1, expiring: 1 },
    })
    vi.mocked(certificateApi.list).mockResolvedValue({
      success: true,
      data: [mockOrder],
    })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Dashboard />
      </MemoryRouter>
    )

    expect(await screen.findByText('证书总数')).toBeInTheDocument()
    await waitFor(() => expect(certificateApi.list).toHaveBeenCalledWith({ limit: 10 }))
    expect(screen.getByText('example.com, www.example.com')).toBeInTheDocument()
    expect(screen.getByText('ISSUED')).toBeInTheDocument()
    expect(screen.getByText('2026-04-02')).toBeInTheDocument()
  })
})
