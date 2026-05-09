import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import CertificateList from './CertificateList'
import { certificateApi } from '../api/certificates'
import { CertificateType, ChallengeType, OrderStatus } from '../types/certificate'
import type { CertificateOrder } from '../types/certificate'

vi.mock('../api/certificates', () => ({
  certificateApi: {
    list: vi.fn(),
    delete: vi.fn(),
  },
}))

const mockOrder: CertificateOrder = {
  id: 18,
  domains: ['example.com'],
  email: 'admin@example.com',
  cert_type: CertificateType.SINGLE,
  challenge_type: ChallengeType.HTTP_01,
  status: OrderStatus.PENDING,
  auto_renew: true,
  created_at: '2026-01-02T03:04:05Z',
  updated_at: '2026-01-02T03:04:05Z',
  is_expired: false,
}

describe('CertificateList', () => {
  it('loads all orders by default', async () => {
    vi.mocked(certificateApi.list).mockResolvedValue({
      success: true,
      data: [mockOrder],
    })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <CertificateList />
      </MemoryRouter>
    )

    await waitFor(() => expect(certificateApi.list).toHaveBeenCalledWith(undefined))
    expect(screen.getByText('example.com')).toBeInTheDocument()
    expect(screen.getByText('PENDING')).toBeInTheDocument()
  })

  it('reloads orders with the selected status filter', async () => {
    const user = userEvent.setup()
    vi.mocked(certificateApi.list).mockResolvedValue({
      success: true,
      data: [],
    })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <CertificateList />
      </MemoryRouter>
    )

    await waitFor(() => expect(certificateApi.list).toHaveBeenCalledWith(undefined))
    await user.click(screen.getByRole('combobox'))
    await user.click(await screen.findByText('已签发'))

    await waitFor(() => {
      expect(certificateApi.list).toHaveBeenLastCalledWith({ status: OrderStatus.ISSUED })
    })
  })
})
