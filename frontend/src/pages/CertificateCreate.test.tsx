import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import CertificateCreate from './CertificateCreate'
import { certificateApi } from '../api/certificates'
import { CertificateType, ChallengeType, OrderStatus } from '../types/certificate'

const navigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => navigate,
  }
})

vi.mock('../api/certificates', () => ({
  certificateApi: {
    create: vi.fn(),
  },
}))

describe('CertificateCreate', () => {
  it('submits normalized domains and navigates to the created order', async () => {
    const user = userEvent.setup()
    vi.mocked(certificateApi.create).mockResolvedValue({
      success: true,
      data: {
        id: 21,
        domains: ['example.com', 'www.example.com'],
        email: 'admin@example.com',
        cert_type: CertificateType.SINGLE,
        challenge_type: ChallengeType.HTTP_01,
        status: OrderStatus.PENDING,
        auto_renew: true,
        created_at: '2026-01-02T03:04:05Z',
        updated_at: '2026-01-02T03:04:05Z',
        is_expired: false,
      },
    })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <CertificateCreate />
      </MemoryRouter>
    )

    await user.type(screen.getByLabelText('域名'), 'example.com, www.example.com')
    await user.type(screen.getByLabelText('联系邮箱'), 'admin@example.com')
    await user.click(screen.getByRole('button', { name: /创建订单/ }))

    await waitFor(() => {
      expect(certificateApi.create).toHaveBeenCalledWith({
        domains: ['example.com', 'www.example.com'],
        email: 'admin@example.com',
        cert_type: CertificateType.SINGLE,
        challenge_type: ChallengeType.HTTP_01,
        auto_renew: true,
      })
    })
    expect(navigate).toHaveBeenCalledWith('/certificates/21')
  })
})
