import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import Settings from './Settings'
import { systemApi } from '../api/system'

vi.mock('../api/system', () => ({
  systemApi: {
    getHealth: vi.fn(),
  },
}))

describe('Settings', () => {
  it('loads and displays system health details', async () => {
    vi.mocked(systemApi.getHealth).mockResolvedValue({
      status: 'healthy',
      service: '1yuanssl-backend',
      version: '0.1.0',
      database: 'healthy',
      mode: 'mvp',
    })

    render(<Settings />)

    expect(await screen.findByText('系统设置')).toBeInTheDocument()
    await waitFor(() => expect(systemApi.getHealth).toHaveBeenCalled())
    expect(screen.getByText('1yuanssl-backend')).toBeInTheDocument()
    expect(screen.getByText('0.1.0')).toBeInTheDocument()
    expect(screen.getByText('Mock ACME 客户端')).toBeInTheDocument()
    expect(screen.getByText(/不保存 SSH 密码/)).toBeInTheDocument()
  })
})
