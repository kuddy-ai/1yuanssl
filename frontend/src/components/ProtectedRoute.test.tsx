import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import ProtectedRoute from './ProtectedRoute'
import { authSession } from '../auth/session'

describe('ProtectedRoute', () => {
  it('redirects unauthenticated users to login', () => {
    render(
      <MemoryRouter initialEntries={['/certificates']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Routes>
          <Route
            path="/certificates"
            element={
              <ProtectedRoute>
                <div>证书管理</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>管理员登录</div>} />
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByText('管理员登录')).toBeInTheDocument()
  })

  it('renders protected content for authenticated users', () => {
    authSession.setToken('dev-admin-token')

    render(
      <MemoryRouter initialEntries={['/certificates']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Routes>
          <Route
            path="/certificates"
            element={
              <ProtectedRoute>
                <div>证书管理</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>管理员登录</div>} />
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByText('证书管理')).toBeInTheDocument()
  })
})
