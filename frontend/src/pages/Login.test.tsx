import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import Login from './Login'
import { authApi } from '../api/auth'
import { authSession } from '../auth/session'

const navigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => navigate,
  }
})

vi.mock('../api/auth', () => ({
  authApi: {
    login: vi.fn(),
  },
}))

describe('Login', () => {
  it('stores the access token and navigates after login', async () => {
    const user = userEvent.setup()
    vi.mocked(authApi.login).mockResolvedValue({
      success: true,
      data: { access_token: 'dev-admin-token', token_type: 'bearer' },
    })

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Login />
      </MemoryRouter>
    )

    await user.type(screen.getByLabelText('用户名'), 'admin')
    await user.type(screen.getByLabelText('密码'), 'admin')
    await user.click(screen.getByRole('button', { name: /登\s*录/ }))

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({ username: 'admin', password: 'admin' })
    })
    expect(authSession.getToken()).toBe('dev-admin-token')
    expect(navigate).toHaveBeenCalledWith('/', { replace: true })
  })
})
